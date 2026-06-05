<template>
  <div class="unified-root">
    <!-- State 1: Upload -->
    <DropZone
      v-if="state === 'upload'"
      @files-selected="onFilesSelected"
    />

    <!-- State 2: Parsing -->
    <ParsingOverlay
      v-else-if="state === 'uploading' || state === 'parsing'"
      :file-name="currentFileName"
      :file-size="formatSize(currentFileSize)"
      :uploaded="formatSize(currentUploaded)"
      :progress="currentProgress"
      :stage="currentStage"
      :phase="state"
    />

    <!-- State 3: Dual Pane -->
    <div v-else class="dual-pane">
      <div class="pane-left">
        <PdfPreview
          ref="pdfRef"
          :doc-id="currentDocId"
          :doc-name="currentDocName"
          :doc-type="currentDocType"
          :highlight-page="highlightPage"
        />
      </div>

      <!-- linking beam -->
      <svg
        v-if="beamVisible"
        class="linking-beam"
        :style="beamContainerStyle"
      >
        <line
          :x1="beamLine.x1"
          :y1="beamLine.y1"
          :x2="beamLine.x2"
          :y2="beamLine.y2"
          stroke="url(#beamGrad)"
          stroke-width="1.5"
          stroke-dasharray="4 2"
          class="beam-line"
        />
        <circle
          :cx="beamLine.x1"
          :cy="beamLine.y1"
          r="2"
          fill="#00d4ff"
          class="beam-dot"
        />
        <circle
          :cx="beamLine.x2"
          :cy="beamLine.y2"
          r="2"
          fill="#7b2ff7"
          class="beam-dot"
        />
        <defs>
          <linearGradient id="beamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#00d4ff" stop-opacity="0.8"/>
            <stop offset="50%" stop-color="#7b2ff7" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#00d4ff" stop-opacity="0.3"/>
          </linearGradient>
        </defs>
      </svg>

      <div class="pane-divider"></div>

      <div class="pane-right">
        <ChatPanel
          :messages="messages"
          :sending="sending"
          :doc-id="currentDocId"
          :hovered-source-idx="hoveredMessageIdx"
          :hovered-source-sub="hoveredSourceIdx"
          @send="onSendMessage"
          @source-hover="onSourceHover"
          @source-leave="onSourceLeave"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useMessage } from 'naive-ui'
import { useAppStore } from '../stores/app'
import { api, type SourceChunk } from '../api'
import DropZone from '../components/DropZone.vue'
import ParsingOverlay from '../components/ParsingOverlay.vue'
import PdfPreview from '../components/PdfPreview.vue'
import ChatPanel from '../components/ChatPanel.vue'

const store = useAppStore()
const message = useMessage()

type AppState = 'upload' | 'uploading' | 'parsing' | 'ready'

const state = ref<AppState>('upload')

const currentDocId = ref<number | null>(null)
const currentDocName = ref('')
const currentDocType = ref('')

interface MessageItem {
  role: 'user' | 'assistant'
  content: string
  sources?: SourceChunk[]
}

const messages = ref<MessageItem[]>([])
const sending = ref(false)
const pdfRef = ref<any>(null)

const hoveredMessageIdx = ref<number | null>(null)
const hoveredSourceIdx = ref<number | null>(null)
const highlightPage = ref<number | null>(null)

const beamVisible = ref(false)
const beamContainerStyle = ref({})
const beamLine = ref({ x1: 0, y1: 0, x2: 0, y2: 0 })

const currentFileName = ref('')
const currentFileSize = ref(0)
const currentUploaded = ref(0)
const currentProgress = ref(0)
const currentStage = ref('')
const currentTaskId = ref('')

const STORAGE_KEY = 'ai_analyse_active_upload'
let pollTimer: ReturnType<typeof setInterval> | null = null
let activeTaskId = ''
let isRecovering = false
let pollAbort = false

const moduleState = {
  fileName: '',
  fileSize: 0,
  progress: 0,
  stage: '',
  taskId: '',
  updatedAt: 0,
}

function saveLocalState(taskId: string, filename: string, fileSize: number, phase: string, uploaded: number, progress: number) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      taskId, filename, fileSize, phase, uploaded, progress, ts: Date.now(),
    }))
  } catch {}
}

function clearLocalState() {
  try { localStorage.removeItem(STORAGE_KEY) } catch {}
}

function readLocalState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const data = JSON.parse(raw)
    if (Date.now() - data.ts > 30 * 60 * 1000) {
      localStorage.removeItem(STORAGE_KEY)
      return null
    }
    return data
  } catch {
    return null
  }
}

async function resumeUpload(file: File): Promise<boolean> {
  if (!activeTaskId || !pollTimer) return false
  const local = readLocalState()
  if (!local || local.filename !== file.name || local.phase !== 'uploading') return false

  currentFileName.value = file.name
  currentFileSize.value = file.size
  currentTaskId.value = local.taskId
  state.value = 'uploading'
  currentStage.value = '恢复上传...'
  try {
    await api.uploadFileForTask(local.taskId, file, {
      onUploadProgress: (loaded, total) => {
        currentUploaded.value = loaded
        currentProgress.value = Math.min(100, Math.round((loaded / total) * 100))
        currentStage.value = '上传文件'
        saveLocalState(local.taskId, file.name, file.size, 'uploading', loaded, currentProgress.value)
      },
    })
    currentStage.value = '上传完成，等待处理'
    currentProgress.value = 100
    saveLocalState(local.taskId, file.name, file.size, 'parsing', file.size, 100)
    state.value = 'parsing'
    await pollUntilComplete(local.taskId, file.name, file.size)
    return true
  } catch (e: any) {
    clearLocalState()
    activeTaskId = ''
    currentTaskId.value = ''
    message.error(`上传失败: ${e?.message || '未知错误'}`)
    state.value = 'upload'
    return true
  }
}

async function startFreshUpload(file: File) {
  currentFileName.value = file.name
  currentFileSize.value = file.size
  currentUploaded.value = 0
  currentProgress.value = 0
  currentStage.value = '准备上传'
  state.value = 'uploading'
  isRecovering = false

  try {
    const task = await api.initUpload(file.name, file.size)
    currentTaskId.value = task.task_id
    saveLocalState(task.task_id, file.name, file.size, 'uploading', 0, 0)

    await api.uploadFileForTask(task.task_id, file, {
      onUploadProgress: (loaded, total) => {
        currentUploaded.value = loaded
        currentProgress.value = Math.min(100, Math.round((loaded / total) * 100))
        currentStage.value = '上传文件'
        saveLocalState(task.task_id, file.name, file.size, 'uploading', loaded, currentProgress.value)
      },
    })

    currentStage.value = '上传完成，等待处理'
    currentProgress.value = 100
    saveLocalState(task.task_id, file.name, file.size, 'parsing', file.size, 100)
    state.value = 'parsing'

    await pollUntilComplete(task.task_id, file.name, file.size)

  } catch (e: any) {
    clearLocalState()
    currentTaskId.value = ''
    const errMsg = e?.message || e?.response?.data?.detail || '未知错误'
    message.error(`上传失败: ${errMsg}`)
    state.value = 'upload'
  }
}

async function onFilesSelected(files: File[]) {
  for (const file of files) {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext !== 'pdf' && ext !== 'docx') {
      message.warning(`不支持的文件类型: .${ext}`)
      continue
    }
    if (file.size > 50 * 1024 * 1024) {
      message.warning(`文件超过 50MB 限制: ${file.name}`)
      continue
    }

    const resumed = await resumeUpload(file)
    if (!resumed) {
      await startFreshUpload(file)
    }
  }
}

async function pollUntilComplete(taskId: string, fileName: string, fileSize: number) {
  if (pollTimer && activeTaskId === taskId) return
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
  activeTaskId = taskId
  moduleState.taskId = taskId
  moduleState.fileName = fileName
  moduleState.fileSize = fileSize
  pollAbort = false
  let totalWait = 0
  const maxWait = 30 * 60 * 1000

  return new Promise<void>((resolve, reject) => {
    pollTimer = setInterval(async () => {
      if (pollAbort) { clearInterval(pollTimer!); pollTimer = null; resolve(); return }
      totalWait += 1500
      if (totalWait > maxWait) { clearInterval(pollTimer!); pollTimer = null; clearLocalState(); activeTaskId = ''; reject(new Error('处理超时')); return }
      try {
        const t = await api.getTask(taskId)
        moduleState.progress = t.progress
        moduleState.stage = t.stage || '处理中'
        moduleState.updatedAt = Date.now()
        currentProgress.value = t.progress
        currentStage.value = t.stage || '处理中'
        saveLocalState(taskId, fileName, fileSize, 'parsing', fileSize, t.progress)

        if (t.status === 'completed' && t.doc_id) {
          clearInterval(pollTimer!); pollTimer = null; activeTaskId = ''; clearLocalState()
          await store.fetchDocuments()
          const doc = store.documents.find(d => d.id === t.doc_id)
          if (doc) {
            currentDocId.value = doc.id; currentDocName.value = doc.original_filename; currentDocType.value = doc.file_type
            store.selectedDocIds = [doc.id]; store.currentDocId = doc.id
          }
          await new Promise(r => setTimeout(r, 500))
          state.value = 'ready'; messages.value = []
          message.success(`"${fileName}" 解析完成`)
          resolve()
        } else if (t.status === 'failed') {
          clearInterval(pollTimer!); pollTimer = null; activeTaskId = ''; clearLocalState()
          reject(new Error(t.error_message || '处理失败'))
        }
      } catch (e: any) {
        clearInterval(pollTimer!); pollTimer = null; activeTaskId = ''; clearLocalState()
        reject(e)
      }
    }, 1500)
  })
}

async function recoverFromLocalOrServer() {
  const local = readLocalState()
  if (local) {
    isRecovering = true
    currentFileName.value = local.filename
    currentFileSize.value = local.fileSize
    currentUploaded.value = local.uploaded || 0
    currentProgress.value = local.progress || 0
    currentStage.value = local.phase === 'uploading' ? '正在上传文件' : '正在处理文件'
    currentTaskId.value = local.taskId
    state.value = local.phase === 'uploading' ? 'uploading' : 'parsing'

    try {
      const t = await api.getTask(local.taskId)
      if (t.status === 'completed' && t.doc_id) {
        await store.fetchDocuments()
        const doc = store.documents.find(d => d.id === t.doc_id)
        if (doc) { currentDocId.value = doc.id; currentDocName.value = doc.original_filename; currentDocType.value = doc.file_type; store.selectedDocIds = [doc.id]; store.currentDocId = doc.id }
        clearLocalState(); state.value = 'ready'; messages.value = []
        message.success(`"${local.filename}" 已完成`)
        isRecovering = false; return
      }
      if (t.status === 'failed') { clearLocalState(); activeTaskId = ''; state.value = 'upload'; message.error(`"${local.filename}" 上次处理失败: ${t.error_message}`); isRecovering = false; return }
      if (t.status === 'pending') { state.value = 'uploading'; currentStage.value = '请重新选择文件继续上传'; isRecovering = false; return }
      if (activeTaskId === t.task_id && pollTimer) { isRecovering = false; return }
      await pollUntilComplete(t.task_id, t.original_filename, t.file_size)
    } catch (e: any) { state.value = 'upload'; clearLocalState() }
    finally { isRecovering = false }
    return
  }

  try {
    const active = await api.getActiveTasks()
    if (active.length === 0) return
    const t = active[0]
    isRecovering = true
    currentFileName.value = t.original_filename
    currentFileSize.value = t.file_size
    currentUploaded.value = t.file_size
    currentProgress.value = t.progress
    currentStage.value = t.stage || '正在处理'
    currentTaskId.value = t.task_id
    state.value = 'parsing'
    saveLocalState(t.task_id, t.original_filename, t.file_size, 'parsing', t.file_size, t.progress)
    if (activeTaskId === t.task_id && pollTimer) { isRecovering = false; return }
    await pollUntilComplete(t.task_id, t.original_filename, t.file_size)
    isRecovering = false
  } catch (e) { state.value = 'upload' }
}

onMounted(async () => {
  await store.fetchDocuments()
  if (activeTaskId && moduleState.taskId === activeTaskId && pollTimer) {
    currentFileName.value = moduleState.fileName
    currentFileSize.value = moduleState.fileSize
    currentProgress.value = moduleState.progress
    currentStage.value = moduleState.stage
    currentTaskId.value = moduleState.taskId
    state.value = 'parsing'
    isRecovering = true
    await pollUntilComplete(moduleState.taskId, moduleState.fileName, moduleState.fileSize)
    isRecovering = false
    return
  }
  await recoverFromLocalOrServer()
})

onBeforeUnmount(() => {
})

async function onSendMessage(q: string) {
  if (!currentDocId.value) return

  messages.value.push({ role: 'user', content: q })
  sending.value = true

  try {
    const res = await api.chat(q, [currentDocId.value])
    messages.value.push({
      role: 'assistant',
      content: res.answer,
      sources: res.sources,
    })
  } catch (e: any) {
    const errMsg = e?.message || e?.response?.data?.detail || '请求失败'
    message.error(errMsg)
    messages.value.push({
      role: 'assistant',
      content: `抱歉，${errMsg}`,
    })
  } finally {
    sending.value = false
  }
}

function onSourceHover(payload: {
  messageIdx: number
  sourceIdx: number
  page: number | null | undefined
  sourceRect: { left: number; top: number; right: number; bottom: number; width: number; height: number } | null
}) {
  hoveredMessageIdx.value = payload.messageIdx
  hoveredSourceIdx.value = payload.sourceIdx
  if (payload.page) {
    highlightPage.value = payload.page
  }

  if (payload.sourceRect && pdfRef.value) {
    const rootRect = document.querySelector('.unified-root')?.getBoundingClientRect()
    if (!rootRect) return

    const sourceCenterY = payload.sourceRect.top + payload.sourceRect.height / 2 - rootRect.top
    const sourceRight = payload.sourceRect.right - rootRect.left

    const pagePos = pdfRef.value.getPagePosition?.(payload.page || 1)
    let targetY = sourceCenterY
    if (pagePos) {
      const pdfContainerRect = pdfRef.value.getViewportRect?.()
      if (pdfContainerRect) {
        targetY = pagePos.top - rootRect.top + (pagePos.bottom - pagePos.top) / 2
      }
    }

    const leftPaneWidth = window.innerWidth / 2
    beamLine.value = {
      x1: sourceRight - 4,
      y1: sourceCenterY,
      x2: leftPaneWidth,
      y2: targetY,
    }
    beamContainerStyle.value = {
      position: 'absolute',
      inset: 0,
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      zIndex: 10,
    }
    beamVisible.value = true
  }
}

function onSourceLeave() {
  hoveredMessageIdx.value = null
  hoveredSourceIdx.value = null
  highlightPage.value = null
  beamVisible.value = false
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.unified-root {
  height: 100%;
  background: #0a0e1a;
  color: rgba(255, 255, 255, 0.8);
  position: relative;
  overflow: hidden;
}

.dual-pane {
  display: flex;
  height: 100%;
  position: relative;
}

.pane-left {
  flex: 1;
  min-width: 0;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
}

.pane-right {
  flex: 1;
  min-width: 0;
  position: relative;
}

.pane-divider {
  width: 1px;
  background: linear-gradient(
    180deg,
    transparent,
    rgba(0, 212, 255, 0.15),
    rgba(123, 47, 247, 0.15),
    transparent
  );
  position: absolute;
  left: 50%;
  top: 10%;
  bottom: 10%;
  transform: translateX(-50%);
  pointer-events: none;
}

.linking-beam {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 10;
  overflow: visible;
}

.beam-line {
  animation: beamDash 1s linear infinite;
}

@keyframes beamDash {
  to {
    stroke-dashoffset: -12;
  }
}

.beam-dot {
  animation: beamDotPulse 1.5s ease-in-out infinite;
}

@keyframes beamDotPulse {
  0%, 100% { opacity: 0.3; r: 2; }
  50% { opacity: 1; r: 3; }
}
</style>

<style>
/* Global dark theme overrides */
html, body, #app {
  background: #0a0e1a !important;
  color: rgba(255, 255, 255, 0.8);
}

/* Override Naive UI layout colors in dark mode */
.n-layout {
  background: #0a0e1a !important;
}
.n-layout-header {
  background: rgba(10, 14, 26, 0.95) !important;
  border-bottom-color: rgba(255, 255, 255, 0.05) !important;
}
.n-layout-content {
  background: #0a0e1a !important;
}
</style>
