'use client'

import { useState, useEffect } from 'react'
import { X, FileText, Heart } from 'lucide-react'
import { getCandidateDetails, shortlistCandidate, rejectCandidate } from '../lib/api'
import { CandidateDetails } from '../types'

interface CandidateProfileProps {
  candidateId: string
  query: string
  onClose: () => void
}

export default function CandidateProfile({ candidateId, query, onClose }: CandidateProfileProps) {
  const [candidate, setCandidate] = useState<CandidateDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadCandidateDetails()
  }, [candidateId])

  const loadCandidateDetails = async () => {
    try {
      const details = await getCandidateDetails(candidateId)
      setCandidate(details)
    } catch (error) {
      console.error('Failed to load candidate details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (action: 'shortlist' | 'reject') => {
    if (!candidate) return
    
    setActionLoading(true)
    try {
      if (action === 'shortlist') {
        await shortlistCandidate(candidateId, !candidate.shortlisted)
        setCandidate({
          ...candidate,
          shortlisted: !candidate.shortlisted
        })
      } else {
        await rejectCandidate(candidateId)
        setCandidate({
          ...candidate,
          status: 'rejected'
        })
      }
    } catch (error) {
      console.error(`Failed to ${action} candidate:`, error)
    } finally {
      setActionLoading(false)
    }
  }

  const highlightQueryTerms = (text: string) => {
    if (!query) return text
    
    const queryTerms = query.toLowerCase().split(/\s+/)
    let highlightedText = text
    
    queryTerms.forEach(term => {
      if (term.length > 2) {
        const regex = new RegExp(`(${term})`, 'gi')
        highlightedText = highlightedText.replace(regex, '<mark class="highlight">$1</mark>')
      }
    })
    
    return <span dangerouslySetInnerHTML={{ __html: highlightedText }} />
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto" style={{backgroundColor: 'var(--surface)'}}>
          <div className="p-6">
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{borderColor: 'var(--primary)'}}></div>
              <span className="ml-3" style={{color: 'var(--text-secondary)'}}>Loading candidate details...</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!candidate) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto" style={{backgroundColor: 'var(--surface)'}}>
          <div className="p-6">
            <h3 className="text-lg font-medium" style={{color: 'var(--text-primary)'}}>Candidate not found</h3>
            <button
              onClick={onClose}
              className="mt-4 inline-flex items-center px-4 py-2 shadow-sm text-sm font-medium rounded-md hover:opacity-80"
              style={{border: '1px solid var(--border)', backgroundColor: 'var(--background)', color: 'var(--text-primary)'}}
            >
              Back to Results
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto" style={{backgroundColor: 'var(--surface)'}}>
        <div className="sticky top-0 px-6 py-4 flex justify-between items-center" style={{backgroundColor: 'var(--surface)', borderBottom: '1px solid var(--border)'}}>
          <h2 className="text-xl font-semibold" style={{color: 'var(--text-primary)'}}>Candidate Profile</h2>
          <button
            onClick={onClose}
            className="hover:opacity-70"
            style={{color: 'var(--text-secondary)'}}
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-2xl font-bold mb-2" style={{color: 'var(--text-primary)'}}>{candidate.name}</h3>
            <p className="mb-4" style={{color: 'var(--text-secondary)'}}>{candidate.email}</p>
            
            <div className="flex flex-wrap gap-4 mb-4">
              <div className="px-3 py-1 rounded-full" style={{backgroundColor: 'var(--background)', border: '1px solid var(--primary)'}}>
                <span className="text-sm font-medium" style={{color: 'var(--primary)'}}>
                  Fit: {Math.round(candidate.fit_score * 100)}%
                </span>
              </div>
              <div className="px-3 py-1 rounded-full" style={{backgroundColor: 'var(--background)', border: '1px solid var(--accent-1)'}}>
                <span className="text-sm font-medium" style={{color: 'var(--accent-1)'}}>
                  Intent: {candidate.intent_count} applications
                </span>
              </div>
              <div className="px-3 py-1 rounded-full" style={{backgroundColor: 'var(--background)', border: '1px solid var(--accent-2)'}}>
                <span className="text-sm font-medium" style={{color: 'var(--accent-2)'}}>
                  Score: {Math.round(candidate.final_score * 100)}%
                </span>
              </div>
            </div>

            {candidate.status && (
              <div className="inline-flex px-3 py-1 rounded-full text-sm font-medium" style={{
                backgroundColor: 'var(--background)',
                border: `1px solid ${candidate.status === 'shortlisted' ? 'var(--accent-2)' : candidate.status === 'rejected' ? '#ef4444' : 'var(--border)'}`,
                color: candidate.status === 'shortlisted' ? 'var(--accent-2)' : candidate.status === 'rejected' ? '#ef4444' : 'var(--text-secondary)'
              }}>
                Status: {candidate.status}
              </div>
            )}
          </div>

          {candidate.resume_url && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold mb-3" style={{color: 'var(--text-primary)'}}>Resume File</h4>
              <a 
                href={candidate.resume_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 rounded-md shadow-sm text-sm font-medium hover:opacity-80"
                style={{border: '1px solid var(--border)', backgroundColor: 'var(--background)', color: 'var(--text-primary)'}}
              >
                <FileText className="h-4 w-4 mr-2" />
                View Resume
              </a>
            </div>
          )}

          {candidate.resume_text && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold mb-3" style={{color: 'var(--text-primary)'}}>Resume</h4>
              <div className="rounded-lg p-4 max-h-64 overflow-y-auto" style={{backgroundColor: 'var(--background)', border: '1px solid var(--border)'}}>
                <pre className="text-sm whitespace-pre-wrap font-mono" style={{color: 'var(--text-secondary)'}}>
                  {highlightQueryTerms(candidate.resume_text)}
                </pre>
              </div>
            </div>
          )}

          <div className="flex gap-3 pt-4" style={{borderTop: '1px solid var(--border)'}}>
            <button
              onClick={() => handleAction('shortlist')}
              disabled={actionLoading}
              className="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
              style={{
                background: candidate.shortlisted ? 'var(--accent-2)' : 'var(--background)',
                color: candidate.shortlisted ? 'var(--background)' : 'var(--accent-2)',
                border: `1px solid var(--accent-2)`
              }}
            >
              {actionLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <Heart className={`h-4 w-4 mr-2 ${candidate.shortlisted ? 'fill-current' : ''}`} />
                  {candidate.shortlisted ? 'Shortlisted' : 'Shortlist'}
                </div>
              )}
            </button>
            
            <button
              onClick={() => handleAction('reject')}
              disabled={actionLoading}
              className="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
              style={{
                background: candidate.status === 'rejected' ? '#ef4444' : 'var(--background)',
                color: candidate.status === 'rejected' ? 'white' : '#ef4444',
                border: '1px solid #ef4444'
              }}
            >
              {actionLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <X className="h-4 w-4 mr-2" />
                  {candidate.status === 'rejected' ? 'Rejected' : 'Reject'}
                </div>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
