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
      error.value = e?.response?.data?.detail || e.message || '获取文档列表失败'
      console.error('fetchDocuments error:', e)
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
      error.value = e?.response?.data?.detail || e.message || '删除失败'
      throw e
    }
  }

  async function uploadFiles(files: File[]) {
    loading.value = true
    error.value = null
    try {
      await api.uploadFiles(files)
      await fetchDocuments()
    } catch (e: any) {
      error.value = e?.response?.data?.detail || e.message || '上传失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    documents, selectedDocIds, loading, error,
    fetchDocuments, deleteDocument, uploadFiles,
  }
})
