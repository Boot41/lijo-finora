import { useState } from 'react'
import { Search, FileText, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAppStore } from '@/store'
import apiService from '@/api'

export default function SearchInterface() {
  const [query, setQuery] = useState('')
  const [limit, setLimit] = useState(5)
  const { 
    searchResults, 
    isSearching, 
    searchQuery,
    setSearchResults, 
    setSearching, 
    setSearchQuery 
  } = useAppStore()

  const handleSearch = async () => {
    if (!query.trim()) return

    try {
      setSearching(true)
      setSearchQuery(query)
      
      const response = await apiService.searchDocuments({ query, limit })
      setSearchResults(response.results)
    } catch (error) {
      console.error('Search failed:', error)
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }

  const quickSearches = [
    { label: 'Summary', query: 'summary overview main points' },
    { label: 'Key Concepts', query: 'key concepts important terms' },
    { label: 'Methodology', query: 'methodology approach methods' },
    { label: 'Conclusions', query: 'conclusions results findings' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Search Documents</h1>
        <p className="mt-2 text-gray-600">
          Search through your uploaded documents using semantic similarity.
        </p>
      </div>

      {/* Search Input */}
      <Card>
        <CardHeader>
          <CardTitle>Search Query</CardTitle>
          <CardDescription>
            Enter your search terms or questions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-2">
            <Input
              placeholder="What are you looking for?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              disabled={isSearching}
              className="flex-1"
            />
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="px-3 py-2 border border-input rounded-md"
              disabled={isSearching}
            >
              <option value={3}>3 results</option>
              <option value={5}>5 results</option>
              <option value={10}>10 results</option>
            </select>
            <Button onClick={handleSearch} disabled={!query.trim() || isSearching}>
              {isSearching ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Quick Search Buttons */}
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-500">Quick searches:</span>
            {quickSearches.map((item) => (
              <Button
                key={item.label}
                variant="outline"
                size="sm"
                onClick={() => {
                  setQuery(item.query)
                  handleSearch()
                }}
                disabled={isSearching}
              >
                {item.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Search Results */}
      {searchQuery && (
        <div>
          <h2 className="text-xl font-semibold mb-4">
            Search Results for "{searchQuery}"
          </h2>
          
          {searchResults.length === 0 && !isSearching && (
            <Card>
              <CardContent className="text-center py-8">
                <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-500">No relevant documents found.</p>
                <p className="text-sm text-gray-400 mt-2">
                  Try different search terms or upload more documents.
                </p>
              </CardContent>
            </Card>
          )}

          <div className="space-y-4">
            {searchResults.map((result, index) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">
                      Result {index + 1}
                    </CardTitle>
                    <div className="text-sm text-gray-500">
                      Similarity: {(result.similarity_score * 100).toFixed(1)}%
                    </div>
                  </div>
                  <CardDescription>
                    {result.metadata.filename && (
                      <span className="font-medium">
                        File: {result.metadata.filename}
                      </span>
                    )}
                    {result.metadata.page_numbers && result.metadata.page_numbers.length > 0 && (
                      <span className="ml-4">
                        Pages: {result.metadata.page_numbers.join(', ')}
                      </span>
                    )}
                    {result.metadata.title && (
                      <span className="ml-4">
                        Section: {result.metadata.title}
                      </span>
                    )}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-gray-700 leading-relaxed">
                      {result.text}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
