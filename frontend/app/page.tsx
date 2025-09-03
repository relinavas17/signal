'use client'

import { useState } from 'react'
import { Search, Users, TrendingUp, Filter } from 'lucide-react'
import SearchResults from './components/SearchResults'
import { searchCandidates } from './lib/api'
import type { Candidate } from './types'

export default function Home() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Candidate[]>([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Starting search for:', query)
    setLoading(true)
    try {
      console.log('Calling searchCandidates API...')
      const searchResults = await searchCandidates(query)
      console.log('Search results:', searchResults)
      setResults(searchResults)
      setHasSearched(true)
    } catch (error) {
      console.error('Search failed:', error)
      console.error('Error details:', error)
      // Show error to user
      alert(`Search failed: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-[1120px] mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4" style={{color: 'var(--text-primary)'}}>
            Source High-Intent Candidates
          </h1>
          <p className="text-lg" style={{color: 'var(--text-secondary)'}}>
            Search the talent pool using to find candidates actively looking for opportunities
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-8">
          <div className="rounded-lg shadow-md p-6" style={{backgroundColor: 'var(--surface)', border: '1px solid var(--border)'}}>
            <div className="flex gap-4">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search (e.g., 3 years analyst Power BI)"
                className="flex-1 px-4 py-2 rounded-lg focus:ring-2 focus:border-transparent"
                style={{
                  backgroundColor: 'var(--background)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-primary)'
                }}
              />
              <button
                type="submit"
                disabled={loading}
                className={`inline-flex items-center gap-2 px-6 py-2 rounded-lg text-white font-medium
                  bg-gradient-to-r from-pink-900 via-purple-500 to-blue-500`}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2" style={{borderColor: 'var(--background)'}}></div>
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4" />
                    Search
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Stats Cards */}
        {!hasSearched && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="overflow-hidden shadow rounded-lg" style={{backgroundColor: 'var(--surface)', border: '1px solid var(--border)'}}>
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Users className="h-6 w-6" style={{color: 'var(--accent-1)'}} />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium truncate" style={{color: 'var(--text-secondary)'}}>
                        Active Candidates
                      </dt>
                      <dd className="text-lg font-medium" style={{color: 'var(--text-primary)'}}>
                        Ready to search
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="overflow-hidden shadow rounded-lg" style={{backgroundColor: 'var(--surface)', border: '1px solid var(--border)'}}>
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6" style={{color: 'var(--primary)'}} />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium truncate" style={{color: 'var(--text-secondary)'}}>
                        AI Scoring
                      </dt>
                      <dd className="text-lg font-medium" style={{color: 'var(--text-primary)'}}>
                        Custom algorithms
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="overflow-hidden shadow rounded-lg" style={{backgroundColor: 'var(--surface)', border: '1px solid var(--border)'}}>
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Filter className="h-6 w-6" style={{color: 'var(--accent-2)'}} />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium truncate" style={{color: 'var(--text-secondary)'}}>
                        Smart Ranking
                      </dt>
                      <dd className="text-lg font-medium" style={{color: 'var(--text-primary)'}}>
                        Semantic Search
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Search Results */}
        {hasSearched && (
          <SearchResults 
            results={results} 
            query={query}
            loading={loading}
          />
        )}

        {/* Example Queries */}
        {!hasSearched && (
          <div className="shadow rounded-lg p-6" style={{backgroundColor: 'var(--surface)', border: '1px solid var(--border)'}}>
            <h3 className="text-lg font-medium mb-4" style={{color: 'var(--text-primary)'}}>
              Try these example searches:
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                "Product Manager with Power BI",
                "Senior data engineer with Python and SQL",
                "Marketing manager with digital campaign experience",
                "Frontend developer React TypeScript",
                "Product manager with B2B SaaS background",
                "DevOps engineer AWS Kubernetes"
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(example)}
                  className="text-left p-3 rounded-lg transition-colors hover:opacity-80"
                  style={{
                    border: '1px solid var(--border)',
                    backgroundColor: 'var(--background)'
                  }}
                >
                  <span className="text-sm" style={{color: 'var(--text-secondary)'}}>"{example}"</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
