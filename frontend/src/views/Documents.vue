<template>
  <div style="padding: 24px; max-width: 1200px; margin: 0 auto;">
    <n-h2>文档管理</n-h2>

    <n-card title="上传文档" style="margin-bottom: 24px;">
      <n-upload
        ref="uploadRef"
        multiple
        :accept="'.pdf,.docx'"
        :max-size="20 * 1024 * 1024"
        :custom-request="handleUpload"
        :default-upload="true"
        list-type="text"
      >
        <n-upload-dragger>
          <div style="padding: 40px 0;">
            <n-icon size="48" color="#18a058">
              <document-outline />
            </n-icon>
            <n-p>拖拽 PDF 或 Word 文件到此处，或点击上传</n-p>
            <n-p depth="3" style="font-size: 12px;">支持 PDF、DOCX，单文件最大 20MB</n-p>
          </div>
        </n-upload-dragger>
      </n-upload>
      <n-card
        v-if="uploading"
        size="small"
        style="margin-top: 12px; background: var(--n-color-target);"
      >
        <n-space vertical :size="8">
          <div style="display: flex; justify-content: space-between; gap: 12px;">
            <span>{{ uploadStatusText }}</span>
            <span>{{ uploadProgress }}%</span>
          </div>
          <n-progress
            type="line"
            :percentage="uploadProgress"
            :processing="uploadProgress < 100 || processingUpload"
            :indicator-placement="'inside'"
          />
          <n-text depth="3" style="font-size: 12px;">
            {{ processingUpload ? '文件已传输完成，服务器正在解析文档并生成向量，请稍候。' : '正在上传文件到服务器。' }}
          </n-text>
        </n-space>
      </n-card>
      <div v-if="store.error" style="color: #d03050; font-size: 13px; margin-top: 12px; padding: 8px; background: #fff1f0; border: 1px solid #ffa39e; border-radius: 4px;">
        ⚠️ 上传失败: {{ store.error }}
      </div>
      <n-button
        v-if="store.documents.length > 0"
        type="primary"
        style="margin-top: 12px;"
        @click="$router.push('/chat')"
      >
        去问答
      </n-button>
    </n-card>

    <n-alert v-if="store.error" type="error" closable style="margin-bottom: 16px;">
      {{ store.error }}
    </n-alert>

    <n-card title="已上传文档">
      <n-data-table
        :columns="columns"
        :data="store.documents"
        :loading="store.loading"
        :pagination="{ pageSize: 10 }"
        :row-key="(row: any) => row.id"
        striped
      />
      <n-empty v-if="!store.loading && store.documents.length === 0" description="暂无文档，请上传 PDF 或 Word 文件" style="padding: 40px 0;" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, h, ref, onMounted } from 'vue'
import { NButton, NTag, useMessage, useDialog, type UploadCustomRequestOptions } from 'naive-ui'
import { DocumentOutline } from '@vicons/ionicons5'
import { useAppStore } from '../stores/app'
import type { DocumentItem } from '../stores/app'

const store = useAppStore()
const message = useMessage()
const dialog = useDialog()
const uploadRef = ref()
const uploading = ref(false)
const processingUpload = ref(false)
const uploadProgress = ref(0)

const uploadStatusText = computed(() => {
  if (processingUpload.value) {
    return '上传完成，正在处理文档'
  }
  return '正在上传文档'
})

onMounted(async () => {
  try {
    await store.fetchDocuments()
  } catch (e: any) {
    console.error('Failed to load documents on mount:', e)
    // Error is already handled in store, just log it here
  }
})

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function handleUpload({ file, onFinish, onError, onProgress }: UploadCustomRequestOptions) {
  try {
    if (!file.file) {
      message.error('文件对象不存在')
      onError()
      return
    }
    
    // Client-side validation
    const maxSize = 20 * 1024 * 1024 // 20MB
    if (file.file.size > maxSize) {
      message.error(`文件大小超过20MB限制（当前：${formatSize(file.file.size)}）`)
      onError()
      return
    }
    
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.file.type)) {
      message.error(`不支持的文件类型：${file.file.type || '未知'}，只支持PDF和DOCX格式`)
      onError()
      return
    }
    
    if (file.file.size === 0) {
      message.error('文件为空，请选择有效的文件')
      onError()
      return
    }
    
    uploading.value = true
    processingUpload.value = false
    uploadProgress.value = 0
    message.loading(`正在上传 "${file.name}"...`, { duration: 0 })
    await store.uploadFiles([file.file], {
      onUploadProgress: (percent) => {
        uploadProgress.value = percent
        onProgress({ percent })
        if (percent >= 100) {
          processingUpload.value = true
          message.destroyAll()
          message.loading(`"${file.name}" 上传完成，正在处理文档...`, { duration: 0 })
        }
      },
    })
    message.destroyAll()
    message.success(`"${file.name}" 上传成功`)
    onFinish()
  } catch (e: any) {
    message.destroyAll()
    const errorMsg = e?.message || store.error || '上传失败，请重试'
    message.error(errorMsg)
    console.error('Upload error:', e)
    onError()
  } finally {
    uploading.value = false
    processingUpload.value = false
    uploadProgress.value = 0
  }
}

function handleDelete(row: DocumentItem) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除 "${row.original_filename}" 吗？此操作不可恢复。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await store.deleteDocument(row.id)
        message.success('删除成功')
      } catch {
        message.error('删除失败')
      }
    },
  })
}

const columns = [
  { title: '文件名', key: 'original_filename', ellipsis: { tooltip: true } },
  {
    title: '类型',
    key: 'file_type',
    width: 80,
    render(row: DocumentItem) {
      return h(NTag, { type: row.file_type === 'pdf' ? 'error' : 'info', size: 'small' }, () => row.file_type.toUpperCase())
    },
  },
  { title: '大小', key: 'file_size', width: 100, render(row: DocumentItem) { return formatSize(row.file_size) } },
  { title: '文本块数', key: 'chunk_count', width: 100 },
  { title: '内容预览', key: 'content_preview', ellipsis: { tooltip: true } },
  { title: '上传时间', key: 'created_at', width: 180, render(row: DocumentItem) { return formatTime(row.created_at) } },
  {
    title: '操作',
    width: 100,
    render(row: DocumentItem) {
      return h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row) }, () => '删除')
    },
  },
]
</script>
