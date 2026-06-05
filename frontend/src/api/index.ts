import axios, { type AxiosProgressEvent } from 'axios'
import type { DocumentItem } from '../stores/app'

const http = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

const UPLOAD_TIMEOUT = 10 * 60 * 1000

http.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

http.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.status)
    return response
  },
  (error) => {
    console.error('API Response Error:', error)
    if (error.code === 'ECONNABORTED') {
      error.message = error.config?.url?.includes('/documents/upload')
        ? '上传或文档处理超时，请稍后重试，或尝试更小的文件'
        : '请求超时，请检查网络连接或稍后重试'
    } else if (error.response) {
      const status = error.response.status
      if (status === 400) {
        error.message = error.response.data?.detail || '请求参数错误'
      } else if (status === 404) {
        error.message = '请求的资源不存在'
      } else if (status === 500) {
        error.message = error.response.data?.detail || '服务器内部错误'
      } else if (status === 413) {
        error.message = '文件大小超过限制'
      }
    } else if (error.request) {
      error.message = '网络连接失败，请检查后端服务是否运行'
    }
    return Promise.reject(error)
  }
)

export interface DocumentListResponse {
  total: number
  items: DocumentItem[]
}

export interface SourceChunk {
  document_id: number
  document_name: string
  content: string
  score: number
  page_number?: number | null
}

export interface ChatResponse {
  answer: string
  sources: SourceChunk[]
}

export interface ChatHistoryItem {
  id: number
  question: string
  answer: string
  source_doc_ids: number[]
  created_at: string
}

export interface UploadFilesOptions {
  onUploadProgress?: (percent: number, loaded?: number, total?: number) => void
  onProgressUpdate?: (stage: string, percent: number) => void
}

export interface UploadTask {
  task_id: string
  original_filename: string
  file_size: number
  status: 'pending' | 'processing' | 'parsing' | 'completed' | 'failed'
  progress: number
  stage: string
  doc_id: number | null
  error_message: string
  created_at: string
  updated_at: string
}

export const api = {
  async initUpload(filename: string, fileSize: number): Promise<UploadTask> {
    const res = await http.post<UploadTask>('/documents/upload/init', null, {
      params: { filename, file_size: fileSize },
    })
    return res.data
  },

  async uploadFileForTask(taskId: string, file: File, options: UploadFilesOptions = {}): Promise<void> {
    const form = new FormData()
    form.append('file', file)
    await http.post(`/documents/upload/${taskId}/file`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: UPLOAD_TIMEOUT,
      onUploadProgress: (event: AxiosProgressEvent) => {
        if (!options.onUploadProgress || !event.total) return
        const percent = Math.min(100, Math.round((event.loaded / event.total) * 100))
        options.onUploadProgress(percent, event.loaded, event.total)
      },
    })
  },

  async getTask(taskId: string): Promise<UploadTask> {
    const res = await http.get<UploadTask>(`/documents/tasks/${taskId}`)
    return res.data
  },

  async getActiveTasks(): Promise<UploadTask[]> {
    const res = await http.get<UploadTask[]>('/documents/tasks/active')
    return res.data
  },

  async deleteTask(taskId: string): Promise<void> {
    await http.delete(`/documents/tasks/${taskId}`)
  },

  async uploadFiles(files: File[], options: UploadFilesOptions = {}): Promise<DocumentItem[]> {
    if (!files || files.length === 0) {
      throw new Error('请选择要上传的文件')
    }

    const results: DocumentItem[] = []
    for (const file of files) {
      const task = await this.initUpload(file.name, file.size)
      options.onProgressUpdate?.('正在上传文件', 0)
      await this.uploadFileForTask(task.task_id, file, {
        onUploadProgress: (p) => options.onProgressUpdate?.('正在上传文件', p),
      })

      const startTime = Date.now()
      while (Date.now() - startTime < 10 * 60 * 1000) {
        const t = await this.getTask(task.task_id)
        options.onProgressUpdate?.(t.stage || '处理中', t.progress)
        if (t.status === 'completed') {
          if (t.doc_id) {
            const list = await this.getDocuments()
            const doc = list.items.find(d => d.id === t.doc_id)
            if (doc) results.push(doc)
          }
          break
        }
        if (t.status === 'failed') {
          throw new Error(t.error_message || '处理失败')
        }
        await new Promise(r => setTimeout(r, 1000))
      }
    }
    return results
  },

  async getDocuments(): Promise<DocumentListResponse> {
    const res = await http.get<DocumentListResponse>('/documents')
    return res.data
  },

  async deleteDocument(id: number): Promise<void> {
    if (!id || id <= 0) throw new Error('无效的文档ID')
    await http.delete(`/documents/${id}`)
  },

  async chat(question: string, docIds: number[]): Promise<ChatResponse> {
    if (!question || !question.trim()) throw new Error('请输入问题')
    if (!docIds || docIds.length === 0) throw new Error('请选择要查询的文档')
    const res = await http.post<ChatResponse>('/chat', { question, doc_ids: docIds })
    return res.data
  },

  async getChatHistory(): Promise<ChatHistoryItem[]> {
    const res = await http.get<ChatHistoryItem[]>('/chat/history')
    return res.data
  },
}
