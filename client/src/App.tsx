import React from 'react'
import { Upload, Search, MessageCircle, FileText, PieChart } from 'lucide-react'
import { Toaster } from 'sonner'
import DocumentUpload from './pages/DocumentUpload'
import SearchInterface from './pages/SearchInterface'
import ChatInterface from './pages/ChatInterface'
import ExpenseCategories from './pages/ExpenseCategories'
import StatusBar from './components/features/StatusBar'

function App() {
  const [activeTab, setActiveTab] = React.useState<'upload' | 'search' | 'chat' | 'expenses'>('upload')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Finora</h1>
            </div>
            <StatusBar />
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'upload'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Upload className="h-4 w-4" />
              <span>Upload Documents</span>
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'search'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Search className="h-4 w-4" />
              <span>Search</span>
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'chat'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <MessageCircle className="h-4 w-4" />
              <span>Chat</span>
            </button>
            <button
              onClick={() => setActiveTab('expenses')}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'expenses'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <PieChart className="h-4 w-4" />
              <span>Expense Categories</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'upload' && <DocumentUpload />}
        {activeTab === 'search' && <SearchInterface />}
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'expenses' && <ExpenseCategories />}
      </main>
      
      {/* Toast notifications */}
      <Toaster position="top-right" richColors />
    </div>
  )
}

export default App
