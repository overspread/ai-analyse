import axios, { type AxiosProgressEvent } from 'axios'
import type { DocumentItem } from '../stores/app'

const http = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

const UPLOAD_TIMEOUT = 10 * 60 * 1000

// Add request interceptor for error handling
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

// Add response interceptor for error handling
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
      // Server responded with error status
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
      // Request made but no response
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
  onUploadProgress?: (percent: number) => void
}

export const api = {
  async uploadFiles(files: File[], options: UploadFilesOptions = {}): Promise<DocumentItem[]> {
    if (!files || files.length === 0) {
      throw new Error('请选择要上传的文件')
    }
    
    const form = new FormData()
    files.forEach(f => form.append('files', f))
    
    try {
      const res = await http.post<DocumentItem[]>('/documents/upload', form, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: UPLOAD_TIMEOUT,
        onUploadProgress: (event: AxiosProgressEvent) => {
          if (!options.onUploadProgress || !event.total) {
            return
          }
          const percent = Math.min(100, Math.round((event.loaded / event.total) * 100))
          options.onUploadProgress(percent)
        },
      })
      return res.data
    } catch (error: any) {
      console.error('Upload files error:', error)
      throw error
    }
  },

  async getDocuments(): Promise<DocumentListResponse> {
    try {
      const res = await http.get<DocumentListResponse>('/documents')
      return res.data
    } catch (error: any) {
      console.error('Get documents error:', error)
      throw error
    }
  },

  async deleteDocument(id: number): Promise<void> {
    if (!id || id <= 0) {
      throw new Error('无效的文档ID')
    }
    
    try {
      await http.delete(`/documents/${id}`)
    } catch (error: any) {
      console.error('Delete document error:', error)
      throw error
    }
  },

  async chat(question: string, docIds: number[]): Promise<ChatResponse> {
    if (!question || !question.trim()) {
      throw new Error('请输入问题')
    }
    if (!docIds || docIds.length === 0) {
      throw new Error('请选择要查询的文档')
    }
    
    try {
      const res = await http.post<ChatResponse>('/chat', { question, doc_ids: docIds })
      return res.data
    } catch (error: any) {
      console.error('Chat error:', error)
      throw error
    }
  },

  async getChatHistory(): Promise<ChatHistoryItem[]> {
    try {
      const res = await http.get<ChatHistoryItem[]>('/chat/history')
      return res.data
    } catch (error: any) {
      console.error('Get chat history error:', error)
      throw error
    }
  },
}
