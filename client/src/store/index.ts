import { create } from 'zustand'

interface Document {
  id: string
  filename: string
  chunks_count: number
  metadata: Record<string, any>
  uploaded_at: string
}

interface SearchResult {
  text: string
  metadata: Record<string, any>
  similarity_score: number
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: Array<{
    filename: string
    pages: number[]
    title: string
    text_preview: string
  }>
}

interface AppState {
  // Documents
  documents: Document[]
  isUploading: boolean
  uploadProgress: number
  
  // Search
  searchResults: SearchResult[]
  isSearching: boolean
  searchQuery: string
  
  // Chat
  messages: ChatMessage[]
  isTyping: boolean
  responseLength: 'brief' | 'balanced' | 'detailed'
  
  // App status
  serverStatus: {
    status: string
    chunk_count: number
    api_key_configured: boolean
  } | null
  
  // Actions
  setDocuments: (documents: Document[]) => void
  addDocument: (document: Document) => void
  clearDocuments: () => void
  setUploading: (isUploading: boolean) => void
  setUploadProgress: (progress: number) => void
  
  setSearchResults: (results: SearchResult[]) => void
  setSearching: (isSearching: boolean) => void
  setSearchQuery: (query: string) => void
  
  addMessage: (message: ChatMessage) => void
  setTyping: (isTyping: boolean) => void
  setResponseLength: (length: 'brief' | 'balanced' | 'detailed') => void
  clearMessages: () => void
  
  setServerStatus: (status: AppState['serverStatus']) => void
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  documents: [],
  isUploading: false,
  uploadProgress: 0,
  
  searchResults: [],
  isSearching: false,
  searchQuery: '',
  
  messages: [],
  isTyping: false,
  responseLength: 'balanced',
  
  serverStatus: null,
  
  // Actions
  setDocuments: (documents) => set({ documents }),
  addDocument: (document) => set((state) => ({ 
    documents: [...state.documents, document] 
  })),
  clearDocuments: () => set({ documents: [] }),
  setUploading: (isUploading) => set({ isUploading }),
  setUploadProgress: (uploadProgress) => set({ uploadProgress }),
  
  setSearchResults: (searchResults) => set({ searchResults }),
  setSearching: (isSearching) => set({ isSearching }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  setTyping: (isTyping) => set({ isTyping }),
  setResponseLength: (responseLength) => set({ responseLength }),
  clearMessages: () => set({ messages: [] }),
  
  setServerStatus: (serverStatus) => set({ serverStatus }),
}))
