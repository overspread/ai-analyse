<template>
  <div class="unified-root">
    <!-- State 1: Upload -->
    <DropZone
      v-if="state === 'upload'"
      @files-selected="onFilesSelected"
    />

    <!-- State 2: Parsing -->
    <ParsingOverlay
      v-else-if="state === 'parsing'"
      :file-name="parsingFileName"
      :file-size="parsingFileSize"
      :progress="parsingProgress"
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
import { ref, computed, nextTick } from 'vue'
import { useMessage } from 'naive-ui'
import { useAppStore } from '../stores/app'
import { api, type SourceChunk } from '../api'
import DropZone from '../components/DropZone.vue'
import ParsingOverlay from '../components/ParsingOverlay.vue'
import PdfPreview from '../components/PdfPreview.vue'
import ChatPanel from '../components/ChatPanel.vue'

const store = useAppStore()
const message = useMessage()

type AppState = 'upload' | 'parsing' | 'ready'

const state = ref<AppState>('upload')

const parsingFileName = ref('')
const parsingFileSize = ref('')
const parsingProgress = ref(0)
let progressTimer: ReturnType<typeof setInterval> | null = null

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

    parsingFileName.value = file.name
    parsingFileSize.value = formatSize(file.size)
    state.value = 'parsing'
    parsingProgress.value = 0

    startProgress()

    try {
      const result = await store.uploadFiles([file])

      stopProgress()
      parsingProgress.value = 100

      if (result && result.length > 0) {
        await store.fetchDocuments()
        const doc = store.documents.find(d => d.original_filename === file.name)
        if (doc) {
          currentDocId.value = doc.id
          currentDocName.value = doc.original_filename
          currentDocType.value = doc.file_type
          store.selectedDocIds = [doc.id]
          store.currentDocId = doc.id
        }
      }

      await new Promise(r => setTimeout(r, 600))

      state.value = 'ready'
      messages.value = []
      message.success(`"${file.name}" 解析完成`)
    } catch (e: any) {
      stopProgress()
      message.error(`解析失败: ${e?.message || '未知错误'}`)
      state.value = 'upload'
    }
  }
}

function startProgress() {
  parsingProgress.value = 0
  progressTimer = setInterval(() => {
    if (parsingProgress.value < 90) {
      parsingProgress.value += 1 + Math.random() * 3
      if (parsingProgress.value > 90) parsingProgress.value = 90
    }
  }, 200)
}

function stopProgress() {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

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
