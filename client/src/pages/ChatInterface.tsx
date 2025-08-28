import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, MessageCircle, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAppStore } from '@/store'
import apiService from '@/api'

export default function ChatInterface() {
  const [message, setMessage] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { 
    messages, 
    isTyping, 
    responseLength,
    addMessage, 
    setTyping, 
    setResponseLength,
    clearMessages 
  } = useAppStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!message.trim() || isTyping) return

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: message,
      timestamp: new Date().toISOString()
    }

    addMessage(userMessage)
    setMessage('')
    setTyping(true)

    try {
      const response = await apiService.chatWithDocuments({
        message: message,
        response_length: responseLength
      })

      const assistantMessage = {
        id: response.message_id,
        role: 'assistant' as const,
        content: response.response,
        timestamp: response.created_at,
        sources: response.sources
      }

      addMessage(assistantMessage)
    } catch (error) {
      console.error('Chat failed:', error)
      const errorMessage = {
        id: Date.now().toString(),
        role: 'assistant' as const,
        content: 'Sorry, I encountered an error while processing your message. Please try again.',
        timestamp: new Date().toISOString()
      }
      addMessage(errorMessage)
    } finally {
      setTyping(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Chat with Documents</h1>
        <p className="mt-2 text-gray-600">
          Ask questions about your uploaded documents and get AI-powered answers.
        </p>
      </div>

      {/* Chat Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Chat Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium">Response Length:</label>
            <select
              value={responseLength}
              onChange={(e) => setResponseLength(e.target.value as 'brief' | 'balanced' | 'detailed')}
              className="px-3 py-1 border border-input rounded-md text-sm"
            >
              <option value="brief">Brief</option>
              <option value="balanced">Balanced</option>
              <option value="detailed">Detailed</option>
            </select>
            <Button
              variant="outline"
              size="sm"
              onClick={clearMessages}
              disabled={messages.length === 0}
            >
              Clear Chat
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Chat Messages */}
      <Card className="h-96 flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageCircle className="h-5 w-5" />
            <span>Conversation</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden">
          <div className="h-full overflow-y-auto space-y-4 pr-2">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <MessageCircle className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                <p>Start a conversation by asking a question about your documents.</p>
                <p className="text-sm mt-2">
                  Try: "What are the main topics covered?" or "Summarize the key findings"
                </p>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs font-medium text-gray-600 mb-2">Sources:</p>
                      <div className="space-y-1">
                        {msg.sources.map((source, index) => (
                          <div key={index} className="text-xs text-gray-600">
                            <div className="flex items-center space-x-1">
                              <FileText className="h-3 w-3" />
                              <span className="font-medium">{source.filename}</span>
                              {source.pages.length > 0 && (
                                <span>• Pages: {source.pages.join(', ')}</span>
                              )}
                            </div>
                            <p className="text-gray-500 italic mt-1">
                              {source.text_preview}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg px-4 py-2">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-gray-600">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </CardContent>
      </Card>

      {/* Message Input */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex space-x-2">
            <Input
              placeholder="Ask a question about your documents..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
              disabled={isTyping}
              className="flex-1"
            />
            <Button 
              onClick={handleSendMessage} 
              disabled={!message.trim() || isTyping}
            >
              {isTyping ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
