export interface CandidateResult {
  candidate_id: string
  name: string
  relevance: number
  fit_score: number
  intent_count: number
  matched_terms: string[]
  snippet: string
  shortlisted: boolean
  status: string
  // Added for ResultCard UI
  email?: string
  resume_url?: string
  resume_text?: string
  summary?: string
  resume_photo_url?: string
}

// UI type returned by GET /api/search
export interface Candidate {
  id: string
  name: string
  email?: string
  summary?: string
  resumeUrl?: string
  // Additional scoring fields from GET /api/search
  relevance?: number
  intentCount?: number
}

export interface SearchRequest {
  query: string
  limit?: number
}

export interface ShortlistRequest {
  candidate_id: string
  shortlisted: boolean
}

export interface RejectRequest {
  candidate_id: string
}

export interface CandidateDetails {
  candidate_id: string
  name: string
  email: string
  resume_url?: string
  resume_text?: string
  intent_count: number
  fit_score: number
  final_score: number
  shortlisted: boolean
  status: string
  fit_explanation?: string
}
