import axios from 'axios'
import { Candidate, CandidateResult, SearchRequest, ShortlistRequest, RejectRequest, CandidateDetails } from '../types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const searchCandidates = async (query: string): Promise<Candidate[]> => {
  try {
    console.log('API call to:', `${API_BASE_URL}/api/search?query=${encodeURIComponent(query || '')}`)
    const response = await api.get<Candidate[]>('/api/search', {
      params: { query }
    })
    
    console.log('API response:', response.data)
    return response.data
  } catch (error: any) {
    console.error('API Error:', error)
    console.error('Error response:', error.response?.data)
    console.error('Error status:', error.response?.status)
    throw new Error(`Search failed: ${error.response?.data?.detail || error.message}`)
  }
}

export const shortlistCandidate = async (candidateId: string, shortlisted: boolean): Promise<void> => {
  await api.post('/api/shortlist', {
    candidate_id: candidateId,
    shortlisted,
  })
}

export const rejectCandidate = async (candidateId: string): Promise<void> => {
  await api.post('/api/reject', {
    candidate_id: candidateId,
  })
}

export const getCandidateDetails = async (candidateId: string): Promise<CandidateDetails> => {
  const response = await api.get(`/api/candidate/${candidateId}`)
  return response.data.candidate.fields
}
