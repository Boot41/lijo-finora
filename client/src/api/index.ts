import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface ServerStatus {
  status: string
  chunk_count: number
  api_key_configured: boolean
}

export interface DocumentInfo {
  filename: string
  chunks_count: number
  metadata: Record<string, any>
  document_id: string
  created_at: string
}

export interface SearchRequest {
  query: string
  limit?: number
}

export interface SearchResult {
  text: string
  metadata: Record<string, any>
  similarity_score: number
}

export interface ChatRequest {
  message: string
  response_length?: 'brief' | 'balanced' | 'detailed'
}

export interface ChatResponse {
  response: string
  sources: Array<{
    filename: string
    pages: number[]
    title: string
    text_preview: string
  }>
  message_id: string
  created_at: string
}

// API functions
export const apiService = {
  // Server status
  getStatus: async (): Promise<ServerStatus> => {
    const response = await api.get('/')
    return response.data
  },

  // Document upload
  uploadFile: async (file: File): Promise<DocumentInfo> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  uploadUrl: async (url: string): Promise<DocumentInfo> => {
    const response = await api.post('/documents/upload-url', { url })
    return response.data
  },

  // Search
  searchDocuments: async (request: SearchRequest): Promise<{ results: SearchResult[], message: string }> => {
    const response = await api.post('/documents/search', request)
    return response.data
  },

  // Chat
  chatWithDocuments: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/chat', request)
    return response.data
  },

  // Chat streaming
  chatStream: async (request: ChatRequest): Promise<ReadableStream> => {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.body) {
      throw new Error('No response body')
    }

    return response.body
  },

  // Database management
  clearDatabase: async (): Promise<{ message: string }> => {
    const response = await api.delete('/documents/database')
    return response.data
  },
}

export default apiService
