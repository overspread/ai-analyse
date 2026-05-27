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
        :default-upload="false"
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
import { h, ref } from 'vue'
import { NButton, NTag, useMessage, useDialog, type UploadCustomRequestOptions } from 'naive-ui'
import { DocumentOutline } from '@vicons/ionicons5'
import { useAppStore } from '../stores/app'
import type { DocumentItem } from '../stores/app'

const store = useAppStore()
const message = useMessage()
const dialog = useDialog()
const uploadRef = ref()

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function handleUpload({ file, onFinish, onError }: UploadCustomRequestOptions) {
  try {
    await store.uploadFiles([file.file])
    message.success(`"${file.name}" 上传成功`)
    onFinish()
  } catch (e: any) {
    message.error(e?.response?.data?.detail || store.error || '上传失败')
    onError()
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
