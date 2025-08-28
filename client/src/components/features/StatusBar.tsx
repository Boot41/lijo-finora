import { useEffect, useState } from 'react'
import { CheckCircle, AlertCircle, Database, Key, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { useAppStore } from '@/store'
import { Button } from '@/components/ui/button'
import apiService from '@/api'

export default function StatusBar() {
  const { serverStatus, setServerStatus, clearDocuments, setSearchResults, clearMessages } = useAppStore()
  const [isClearing, setIsClearing] = useState(false)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await apiService.getStatus()
        setServerStatus(status)
      } catch (error) {
        console.error('Failed to fetch server status:', error)
        setServerStatus({
          status: 'error',
          chunk_count: 0,
          api_key_configured: false
        })
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [setServerStatus])

  if (!serverStatus) {
    return (
      <div className="flex items-center space-x-2 text-gray-500">
        <AlertCircle className="h-4 w-4" />
        <span className="text-sm">Loading...</span>
      </div>
    )
  }

  const handleClearDatabase = async () => {
    if (!window.confirm('Are you sure you want to clear all documents from the database? This action cannot be undone.')) {
      return
    }

    const toastId = toast.loading('Clearing database...', {
      description: 'Removing all documents and chunks'
    })

    try {
      setIsClearing(true)
      await apiService.clearDatabase()
      
      // Clear all related state
      clearDocuments()
      setSearchResults([])
      clearMessages()
      
      // Immediately update UI to show 0 chunks
      console.log('Before clear - serverStatus:', serverStatus)
      if (serverStatus) {
        const newStatus = {
          ...serverStatus,
          chunk_count: 0
        }
        console.log('Setting serverStatus to:', newStatus)
        setServerStatus(newStatus)
      }
      
      // Refresh server status to confirm
      console.log('Fetching fresh server status...')
      const status = await apiService.getStatus()
      console.log('Fresh server status:', status)
      setServerStatus(status)
      
      toast.success('Database cleared successfully', {
        id: toastId,
        description: `Database has been cleared`
      })
    } catch (error) {
      console.error('Failed to clear database:', error)
      toast.error('Failed to clear database', {
        id: toastId,
        description: error instanceof Error ? error.message : 'An error occurred'
      })
    } finally {
      setIsClearing(false)
    }
  }

  return (
    <div className="flex items-center space-x-4 text-sm">
      {/* Server Status */}
      <div className="flex items-center space-x-1">
        {serverStatus.status === 'running' ? (
          <CheckCircle className="h-4 w-4 text-green-500" />
        ) : (
          <AlertCircle className="h-4 w-4 text-red-500" />
        )}
        <span className={serverStatus.status === 'running' ? 'text-green-600' : 'text-red-600'}>
          {serverStatus.status === 'running' ? 'Online' : 'Offline'}
        </span>
      </div>

      {/* Document Count */}
      <div className="flex items-center space-x-1 text-gray-600">
        <Database className="h-4 w-4" />
        <span>{serverStatus?.chunk_count || 0} chunks</span>
      </div>

      {/* API Key Status */}
      <div className="flex items-center space-x-1">
        <Key className="h-4 w-4" />
        <span className={serverStatus.api_key_configured ? 'text-green-600' : 'text-orange-600'}>
          {serverStatus.api_key_configured ? 'API Ready' : 'API Missing'}
        </span>
      </div>

      {/* Clear Database Button */}
      {(serverStatus?.chunk_count || 0) > 0 && (
        <Button
          variant="outline"
          size="sm"
          onClick={handleClearDatabase}
          disabled={isClearing}
          className="flex items-center space-x-1 text-red-600 hover:text-red-700 hover:bg-red-50"
        >
          <Trash2 className="h-3 w-3" />
          <span>{isClearing ? 'Clearing...' : 'Clear DB'}</span>
        </Button>
      )}
    </div>
  )
}
