import { useState, useEffect } from 'react'
import { PieChart, DollarSign, Check, X, Edit3, Calendar } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { useAppStore } from '../store'
import { analyzeExpenses, updateTransactionCategory } from '../api'

interface Transaction {
  id: string
  date: string
  description: string
  amount: number
  type: 'debit' | 'credit'
  category: string
  confidence: number
}

interface CategorySummary {
  name: string
  total: number
  count: number
  percentage: number
  color: string
  icon: string
}

const CATEGORY_COLORS = {
  'Food & Dining': 'bg-red-100 text-red-800 border-red-200',
  'Transportation': 'bg-blue-100 text-blue-800 border-blue-200',
  'Shopping': 'bg-purple-100 text-purple-800 border-purple-200',
  'Bills & Utilities': 'bg-yellow-100 text-yellow-800 border-yellow-200',
  'Healthcare': 'bg-green-100 text-green-800 border-green-200',
  'Entertainment': 'bg-pink-100 text-pink-800 border-pink-200',
  'Travel': 'bg-indigo-100 text-indigo-800 border-indigo-200',
  'Income': 'bg-emerald-100 text-emerald-800 border-emerald-200',
  'Transfers': 'bg-gray-100 text-gray-800 border-gray-200',
  'Miscellaneous': 'bg-orange-100 text-orange-800 border-orange-200'
}

const CATEGORY_ICONS = {
  'Food & Dining': '🍽️',
  'Transportation': '🚗',
  'Shopping': '🛍️',
  'Bills & Utilities': '💡',
  'Healthcare': '🏥',
  'Entertainment': '🎬',
  'Travel': '✈️',
  'Income': '💰',
  'Transfers': '🔄',
  'Miscellaneous': '📋'
}

export default function ExpenseCategories() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [categories, setCategories] = useState<CategorySummary[]>([])
  const [loading, setLoading] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [viewMode, setViewMode] = useState<'tiles' | 'transactions'>('tiles')
  const [selectedCategoryForView, setSelectedCategoryForView] = useState<string>('')
  const [sortBy, setSortBy] = useState<'date' | 'amount'>('date')
  const { serverStatus } = useAppStore()

  useEffect(() => {
    if (serverStatus?.chunk_count && serverStatus.chunk_count > 0) {
      loadExpenseAnalysis()
    }
  }, [serverStatus?.chunk_count]) // Only watch chunk_count, not entire serverStatus

  const loadExpenseAnalysis = async () => {
    setLoading(true)
    try {
      const data = await analyzeExpenses()
      setTransactions(data.transactions || [])
      setCategories(calculateCategorySummary(data.transactions || []))
      toast.success('Expense analysis loaded successfully')
    } catch (error) {
      console.error('Failed to load expense analysis:', error)
      toast.error('Failed to load expense analysis')
    } finally {
      setLoading(false)
    }
  }

  const calculateCategorySummary = (transactions: Transaction[]): CategorySummary[] => {
    const categoryMap = new Map<string, { total: number; count: number }>()
    const totalAmount = transactions.reduce((sum, t) => sum + t.amount, 0)
    
    transactions.forEach(transaction => {
      const category = transaction.category
      const existing = categoryMap.get(category) || { total: 0, count: 0 }
      categoryMap.set(category, {
        total: existing.total + transaction.amount,
        count: existing.count + 1
      })
    })

    return Array.from(categoryMap.entries()).map(([name, data]) => ({
      name,
      total: data.total,
      count: data.count,
      percentage: totalAmount > 0 ? (data.total / totalAmount) * 100 : 0,
      color: CATEGORY_COLORS[name as keyof typeof CATEGORY_COLORS] || CATEGORY_COLORS.Miscellaneous,
      icon: CATEGORY_ICONS[name as keyof typeof CATEGORY_ICONS] || '📋'
    })).sort((a, b) => b.total - a.total)
  }

  const handleCategoryUpdate = async (transactionId: string, newCategory: string) => {
    try {
      await updateTransactionCategory(transactionId, newCategory)
      setTransactions(prev => 
        prev.map(t => t.id === transactionId ? { ...t, category: newCategory } : t)
      )
      setCategories(calculateCategorySummary(transactions))
      setEditingTransaction(null)
      toast.success('Category updated successfully')
    } catch (error) {
      console.error('Failed to update category:', error)
      toast.error('Failed to update category')
    }
  }

  const handleCategoryClick = (categoryName: string) => {
    setSelectedCategoryForView(categoryName)
    setViewMode('transactions')
  }

  const handleBackToTiles = () => {
    setViewMode('tiles')
    setSelectedCategoryForView('')
  }

  const totalExpenses = categories.reduce((sum, cat) => sum + cat.total, 0)
  
  const filteredTransactions = transactions.filter(transaction => {
    if (viewMode === 'transactions' && selectedCategoryForView) {
      return transaction.category === selectedCategoryForView
    }
    return true
  })

  const sortedTransactions = [...filteredTransactions].sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(b.date).getTime() - new Date(a.date).getTime()
      case 'amount':
        return b.amount - a.amount
      default:
        return 0
    }
  })

  if (serverStatus?.chunk_count === 0) {
    return (
      <div className="text-center py-12">
        <PieChart className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Documents Uploaded</h3>
        <p className="text-gray-500">Upload bank statements or receipts to analyze your expenses</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Expense Categories</h2>
          <p className="text-gray-600">AI-powered transaction categorization and analysis</p>
        </div>
        <button
          onClick={loadExpenseAnalysis}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Refresh Analysis'}
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Analyzing transactions with AI...</p>
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center">
                <DollarSign className="h-8 w-8 text-red-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Expenses</p>
                  <p className="text-2xl font-bold text-gray-900">₹{totalExpenses.toLocaleString()}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center">
                <Calendar className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Transactions</p>
                  <p className="text-2xl font-bold text-gray-900">{transactions.length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center">
                <Check className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Classified</p>
                  <p className="text-2xl font-bold text-green-900">{transactions.length - filteredTransactions.filter(t => t.category === 'Miscellaneous').length}</p>
                  <p className="text-xs text-gray-500">{((transactions.length - filteredTransactions.filter(t => t.category === 'Miscellaneous').length) / transactions.length * 100).toFixed(1)}% classified</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center">
                <X className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Need Review</p>
                  <p className="text-2xl font-bold text-orange-900">{filteredTransactions.filter(t => t.category === 'Miscellaneous').length}</p>
                  <p className="text-xs text-gray-500">Low confidence/Misc</p>
                </div>
              </div>
            </div>
          </div>

          {/* Category Tiles */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            {!loading && categories.length > 0 && viewMode === 'tiles' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {categories.map((category) => (
                  <div
                    key={category.name}
                    onClick={() => handleCategoryClick(category.name)}
                    className={`p-6 rounded-xl border-2 transition-all duration-200 hover:shadow-lg cursor-pointer transform hover:scale-105 ${
                      CATEGORY_COLORS[category.name as keyof typeof CATEGORY_COLORS] || CATEGORY_COLORS.Miscellaneous
                    }`}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className="text-3xl">
                          {CATEGORY_ICONS[category.name as keyof typeof CATEGORY_ICONS] || '📋'}
                        </span>
                        <h3 className="font-semibold text-xl">{category.name}</h3>
                      </div>
                      <span className="text-sm font-medium px-3 py-1 bg-white bg-opacity-50 rounded-full">
                        {category.count} txns
                      </span>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm opacity-75">Total Spent</span>
                        <span className="font-bold text-2xl">₹{category.total.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm opacity-75">Percentage</span>
                        <span className="font-medium text-lg">{category.percentage.toFixed(1)}%</span>
                      </div>
                      <div className="mt-4 text-center">
                        <span className="text-xs opacity-60">Click to view transactions</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* Transaction List View */}
        {!loading && viewMode === 'transactions' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={handleBackToTiles}
                    className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
                  >
                    <span>←</span>
                    <span>Back to Categories</span>
                  </button>
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">
                      {CATEGORY_ICONS[selectedCategoryForView as keyof typeof CATEGORY_ICONS] || '📋'}
                    </span>
                    <h2 className="text-2xl font-semibold">{selectedCategoryForView}</h2>
                  </div>
                </div>
                <div className="flex gap-3">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'date' | 'amount')}
                    className="px-3 py-2 border rounded-lg text-sm"
                  >
                    <option value="date">Sort by Date</option>
                    <option value="amount">Sort by Amount</option>
                  </select>
                </div>
              </div>
              <div className="text-sm text-gray-500">
                {filteredTransactions.length} transactions in {selectedCategoryForView}
              </div>
            </div>
            <div className="divide-y max-h-96 overflow-y-auto">
              {sortedTransactions.map((transaction) => (
                <div key={transaction.id} className="p-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">{transaction.date}</span>
                      </div>
                      <p className="font-medium">{transaction.description}</p>
                      <p className="text-sm text-gray-600">₹{transaction.amount.toFixed(2)}</p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className={`font-semibold ${transaction.type === 'debit' ? 'text-red-600' : 'text-green-600'}`}>
                          {transaction.type === 'debit' ? '-' : '+'}₹{Math.abs(transaction.amount).toLocaleString()}
                        </p>
                        <div className="flex items-center space-x-2">
                          {editingTransaction === transaction.id ? (
                            <div className="flex items-center space-x-2">
                              <select
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                className="text-xs border rounded px-2 py-1"
                              >
                                <option value="">Select category</option>
                                {Object.keys(CATEGORY_COLORS).map(cat => (
                                  <option key={cat} value={cat}>{cat}</option>
                                ))}
                              </select>
                              <button
                                onClick={() => handleCategoryUpdate(transaction.id, selectedCategory)}
                                className="text-green-600 hover:text-green-700"
                                disabled={!selectedCategory}
                              >
                                <Check className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => setEditingTransaction(null)}
                                className="text-red-600 hover:text-red-700"
                              >
                                <X className="h-4 w-4" />
                              </button>
                            </div>
                          ) : (
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium border ${CATEGORY_COLORS[transaction.category as keyof typeof CATEGORY_COLORS] || CATEGORY_COLORS.Miscellaneous}`}>
                                {transaction.category}
                              </span>
                              <button
                                onClick={() => {
                                  setEditingTransaction(transaction.id)
                                  setSelectedCategory(transaction.category)
                                }}
                                className="text-gray-400 hover:text-gray-600"
                                title="Edit category"
                              >
                                <Edit3 className="h-4 w-4" />
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
    </div>
  )
}
