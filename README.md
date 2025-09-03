# Signal

A 2-screen web application that helps recruiters surface genuine, high-intent candidates using AI-powered scoring and natural language search.

## Overview

Signal combines **Intent** (how often candidates apply) with **Fit** (semantic/contextual match) to rank candidates effectively. Recruiters can search using natural language queries like "3 years analyst working with Power BI" and get ranked results with actionable insights.

### Key Features

- **AI-Powered Scoring**: Combines application frequency (intent) with semantic similarity (fit)
- **Natural Language Search**: Query candidates using conversational language
- **Real-time Ranking**: Server-side scoring with semantic embeddings
- **Airtable Integration**: Persistent storage with easy data management
- **Actionable UI**: Shortlist/reject candidates with one click

## Tech Stack

- **Frontend**: Next.js + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Embeddings**: OpenAI text-embedding-3-small
- **Database**: Airtable (REST API)
- **Optional**: Phidata agents for fit explanations

## Quick Start

### 1. Airtable Setup

Create a new Airtable base with these tables:

**Candidates Table:**
- `candidate_id` (Primary key, text)
- `name` (text)
- `email` (text)
- `resume_url` (text)
- `resume_text` (long text)
- `resume_embedding` (long text, JSON array)
- `intent_count` (number)
- `fit_score` (number, 0-1)
- `final_score` (number, 0-1)
- `shortlisted` (checkbox)
- `status` (single select: Active | Rejected)
- `fit_explanation` (long text, optional)

**Applications Table:**
- `application_id` (Primary key)
- `candidate` (link to Candidates)
- `role_title` (text)
- `role_family` (text)
- `applied_at` (date/time)

### 2. Environment Setup

Create `.env` file in the backend directory:

```env
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_CANDIDATES=Candidates
AIRTABLE_TABLE_APPLICATIONS=Applications

OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL=text-embedding-3-small
MAX_RESULTS=20
INTENT_CAP=5
RELEVANCE_ALPHA=0.6
FINAL_SCORE_WEIGHT=0.4

# Optional agent features
PHIDATA_ENABLED=false
AGENT_MODEL=gpt-4o
```

### 3. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 5. Access the Application

Open http://localhost:3000 in your browser.

## API Reference

### POST /api/ingest_application

Creates or updates a candidate and their application.

**Request:**
```json
{
  "candidate_id": "C-123",
  "name": "Jane Doe",
  "email": "jane@example.com",
  "resume_url": "https://...",
  "resume_text": "optional",
  "role_title": "Data Analyst",
  "role_family": "Analyst",
  "applied_at": "2025-08-31T14:00:00Z"
}
```

### POST /api/search

Search and rank candidates using natural language.

**Request:**
```json
{
  "query": "3 years analyst working with powerbi",
  "limit": 20
}
```

**Response:**
```json
[
  {
    "candidate_id": "C-123",
    "name": "Jane Doe",
    "relevance": 0.87,
    "fit_score": 0.82,
    "intent_count": 3,
    "matched_terms": ["power bi", "analyst"],
    "snippet": "… built dashboards in Power BI for …"
  }
]
```

### POST /api/shortlist

Toggle candidate shortlist status.

**Request:**
```json
{
  "candidate_id": "C-123",
  "shortlisted": true
}
```

### POST /api/reject

Reject a candidate.

**Request:**
```json
{
  "candidate_id": "C-123"
}
```

## Scoring Algorithm

The system uses a multi-factor scoring approach:

1. **Intent Score**: `intent_norm = min(intent_count / 5, 1.0)`
2. **Fit Score**: Cosine similarity between resume and query embeddings
3. **Final Score**: `0.5 * intent_norm + 0.5 * fit_score`
4. **Relevance**: `0.6 * semantic_similarity + 0.4 * final_score`
5. **Term Boosts**: +0.05 per matched term (max +0.1 total)

## Optional: Resume Analyzer Agent

Enable AI-powered fit explanations by setting `PHIDATA_ENABLED=true`. This uses Phidata agents to generate structured explanations of candidate fit including:

- Summary of candidate strengths
- Top matched skills
- Potential gaps

## Roadmap

- Multi-role support
- Interview scheduling agents
- Email automation
- Advanced analytics dashboard
- Bulk candidate import
- Integration with major ATS platforms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
