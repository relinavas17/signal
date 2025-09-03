'use client'

import { useState } from 'react'
import { Copy, Check, Download } from 'lucide-react'
import type { Candidate } from '../types'

interface SearchResultsProps {
  results: Candidate[]
  query: string
  loading: boolean
}

export default function SearchResults({ results, query, loading }: SearchResultsProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null)

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-gray-600">Searching candidates...</span>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="mt-2 text-sm font-medium text-gray-900">No candidates match your search.</h3>
        <p className="mt-1 text-sm text-gray-500">
          Try adjusting your search query or check if candidates have been added to the system.
        </p>
      </div>
    )
  }

  const handleCopyEmail = async (email: string, id: string) => {
    try {
      await navigator.clipboard.writeText(email)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (e) {
      console.error('Clipboard copy failed', e)
    }
  }

  return (
    <div className="space-y-4">
      {results.map((candidate) => (
        <div
          key={candidate.id}
          className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start gap-4">
            {/* Main column */}
            <div className="flex-1 min-w-0">
              {/* Name */}
              <h3 className="text-lg font-semibold text-gray-900 truncate" title={candidate.name}>
                {candidate.name || 'No name provided'}
              </h3>
              {/* Relevance and Intent (below name) */}
              {(typeof candidate.relevance === 'number' || typeof candidate.intentCount === 'number') && (
               <div className="mt-0.8 text-sm">
               {typeof candidate.relevance === 'number' && (
                 <span className="text-green-800">
                   Relevance: {(candidate.relevance * 100).toFixed(0)}%
                 </span>
               )}
             
               {typeof candidate.relevance === 'number' && typeof candidate.intentCount === 'number' && (
                 <span className="text-gray-400 px-1"> • </span>
               )}
             
               {typeof candidate.intentCount === 'number' && (
                 <span className="text-orange-800">
                   Intent: {candidate.intentCount}
                 </span>
               )}
             </div>
             
              )}

              {/* Email + copy */}
              <div className="flex items-center flex-wrap gap-2 mt-1 mb-3">
                {candidate.email ? (
                  <a
                    href={`mailto:${candidate.email}`}
                    aria-label="Email candidate"
                    className="text-black underline underline-offset-2 hover:text-black focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
                  >
                    {candidate.email}
                  </a>
                ) : (
                  <span className="text-gray-500">No email provided</span>
                )}
                {candidate.email && (
                  <button
                    type="button"
                    onClick={() => handleCopyEmail(candidate.email!, candidate.id)}
                    className="inline-flex items-center p-1.5 rounded border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    aria-label="Copy email"
                  >
                    {copiedId === candidate.id ? (
                      <Check className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </button>
                )}
                {/* Inline copied feedback */}
                <span aria-live="polite" className="text-xs text-green-700">
                  {copiedId === candidate.id ? 'Email copied' : ''}
                </span>
              </div>

              {/* Summary - always show full text, no toggle */}
              <div className="mb-2">
                <div className="text-sm text-gray-700 whitespace-pre-wrap">
                  {candidate.summary || 'No summary available.'}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex-shrink-0">
              {candidate.resumeUrl ? (
                <a
                  href={candidate.resumeUrl}
                  target="_blank"
                  rel="noopener"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  aria-label="Download resume"
                >
                  <Download className="h-4 w-4" />
                  Download Resume
                </a>
              ) : (
                <button
                  type="button"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-gray-500 bg-gray-200 cursor-not-allowed"
                  aria-label="Download resume"
                  aria-disabled="true"
                  title="No resume attached"
                >
                  <Download className="h-4 w-4" />
                  Download Resume
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
