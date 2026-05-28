import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'

export interface DocumentItem {
  id: number
  original_filename: string
  file_type: string
  file_size: number
  chunk_count: number
  content_preview: string
  created_at: string
}

export const useAppStore = defineStore('app', () => {
  const documents = ref<DocumentItem[]>([])
  const selectedDocIds = ref<number[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchDocuments() {
    loading.value = true
    error.value = null
    try {
      const res = await api.getDocuments()
      documents.value = res.items || []
    } catch (e: any) {
      const errorMsg = e?.message || e?.response?.data?.detail || '获取文档列表失败'
      error.value = errorMsg
      console.error('fetchDocuments error:', e)
      throw new Error(errorMsg)
    } finally {
      loading.value = false
    }
  }

  async function deleteDocument(id: number) {
    try {
      await api.deleteDocument(id)
      documents.value = documents.value.filter(d => d.id !== id)
      selectedDocIds.value = selectedDocIds.value.filter(d => d !== id)
    } catch (e: any) {
      const errorMsg = e?.message || e?.response?.data?.detail || '删除失败'
      error.value = errorMsg
      console.error('deleteDocument error:', e)
      throw new Error(errorMsg)
    }
  }

  async function uploadFiles(files: File[]) {
    loading.value = true
    error.value = null
    try {
      const result = await api.uploadFiles(files)
      console.log('Upload result:', result)
      await fetchDocuments()
    } catch (e: any) {
      const errorMsg = e?.message || e?.response?.data?.detail || '上传失败'
      error.value = errorMsg
      console.error('uploadFiles error:', e)
      throw new Error(errorMsg)
    } finally {
      loading.value = false
    }
  }

  return {
    documents, selectedDocIds, loading, error,
    fetchDocuments, deleteDocument, uploadFiles,
  }
})
