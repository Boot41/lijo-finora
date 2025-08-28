import React, { useState, useCallback } from 'react'
import { Upload, FileText, Link, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import apiService from '@/api'
import { useAppStore } from '@/store'

export default function DocumentUpload() {
  const [dragActive, setDragActive] = useState(false)
  const [url, setUrl] = useState('')
  const { isUploading, uploadProgress, addDocument, setUploading, setUploadProgress, setServerStatus } = useAppStore()

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFileUpload(e.dataTransfer.files[0])
    }
  }, [])

  const handleFileUpload = async (file: File) => {
    const toastId = toast.loading(`Uploading ${file.name}...`, {
      description: 'Processing document and generating embeddings'
    })

    try {
      setUploading(true)
      setUploadProgress(0)

      const result = await apiService.uploadFile(file)
      
      addDocument({
        id: result.document_id,
        filename: result.filename,
        chunks_count: result.chunks_count,
        metadata: result.metadata,
        uploaded_at: result.created_at.toString()
      })

      setUploadProgress(100)
      
      // Refresh server status to update chunk count and clear DB button
      const status = await apiService.getStatus()
      setServerStatus(status)
      
      toast.success(`Successfully uploaded ${file.name}`, {
        id: toastId,
        description: `Generated ${result.chunks_count} chunks`
      })
    } catch (error) {
      console.error('Upload failed:', error)
      toast.error('Upload failed', {
        id: toastId,
        description: error instanceof Error ? error.message : 'An error occurred during upload'
      })
    } finally {
      setUploading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }

  const handleUrlUpload = async () => {
    if (!url.trim()) {
      toast.error('Please enter a valid URL')
      return
    }

    const toastId = toast.loading('Processing URL...', {
      description: 'Fetching and processing document from URL'
    })

    try {
      setUploading(true)
      const result = await apiService.uploadUrl(url)
      
      addDocument({
        id: result.document_id,
        filename: result.filename,
        chunks_count: result.chunks_count,
        metadata: result.metadata,
        uploaded_at: result.created_at.toString()
      })

      setUrl('')
      
      // Refresh server status to update chunk count and clear DB button
      const status = await apiService.getStatus()
      setServerStatus(status)
      
      toast.success('Successfully processed URL', {
        id: toastId,
        description: `Generated ${result.chunks_count} chunks from ${result.filename}`
      })
    } catch (error) {
      console.error('URL upload failed:', error)
      toast.error('Failed to process URL', {
        id: toastId,
        description: error instanceof Error ? error.message : 'An error occurred while processing the URL'
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Documents</h1>
        <p className="mt-2 text-gray-600">
          Upload documents to build your knowledge base for search and chat.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* File Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5" />
              <span>File Upload</span>
            </CardTitle>
            <CardDescription>
              Upload PDF, DOCX, TXT, or MD files
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div
              className={`relative border-2 border-dashed rounded-lg p-6 transition-colors ${
                dragActive
                  ? 'border-blue-400 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-4">
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <span className="mt-2 block text-sm font-medium text-gray-900">
                      Drop files here or click to upload
                    </span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept=".pdf,.docx,.txt,.md"
                      onChange={(e) => {
                        if (e.target.files?.[0]) {
                          handleFileUpload(e.target.files[0])
                        }
                      }}
                    />
                  </label>
                  <p className="mt-1 text-xs text-gray-500">
                    PDF, DOCX, TXT, MD up to 10MB
                  </p>
                </div>
              </div>

              {isUploading && (
                <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center rounded-lg">
                  <div className="text-center">
                    <Loader2 className="mx-auto h-8 w-8 animate-spin text-blue-600" />
                    <p className="mt-2 text-sm text-gray-600">
                      Processing document... {uploadProgress}%
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* URL Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Link className="h-5 w-5" />
              <span>URL Upload</span>
            </CardTitle>
            <CardDescription>
              Process documents from web URLs
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Input
                type="url"
                placeholder="https://example.com/document.pdf"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isUploading}
              />
            </div>
            <Button 
              onClick={handleUrlUpload}
              disabled={!url.trim() || isUploading}
              className="w-full"
            >
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Process URL
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Upload Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• Supported formats: PDF, DOCX, TXT, MD</li>
            <li>• Maximum file size: 10MB</li>
            <li>• Documents are automatically processed and chunked for optimal search</li>
            <li>• URLs should point directly to downloadable documents</li>
            <li>• Processing time depends on document size and complexity</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
