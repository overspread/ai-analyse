import axios from 'axios'
import type { DocumentItem } from '../stores/app'

const http = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export interface DocumentListResponse {
  total: number
  items: DocumentItem[]
}

export interface SourceChunk {
  document_id: number
  document_name: string
  content: string
  score: number
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

export const api = {
  async uploadFiles(files: File[]): Promise<DocumentItem[]> {
    const form = new FormData()
    files.forEach(f => form.append('files', f))
    const res = await http.post<DocumentItem[]>('/documents/upload', form)
    return res.data
  },

  async getDocuments(): Promise<DocumentListResponse> {
    const res = await http.get<DocumentListResponse>('/documents')
    return res.data
  },

  async deleteDocument(id: number): Promise<void> {
    await http.delete(`/documents/${id}`)
  },

  async chat(question: string, docIds: number[]): Promise<ChatResponse> {
    const res = await http.post<ChatResponse>('/chat', { question, doc_ids: docIds })
    return res.data
  },

  async getChatHistory(): Promise<ChatHistoryItem[]> {
    const res = await http.get<ChatHistoryItem[]>('/chat/history')
    return res.data
  },
}
