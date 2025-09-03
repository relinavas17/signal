from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import requests
import re

load_dotenv()

app = FastAPI(title="Signal API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY") or os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_CANDIDATES = os.getenv("AIRTABLE_TABLE_CANDIDATES", "Candidates")

# Airtable headers
AIRTABLE_HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 20

class CandidateResult(BaseModel):
    candidate_id: str
    name: str
    relevance: float
    fit_score: float
    intent_count: int
    matched_terms: List[str]
    snippet: str
    shortlisted: bool
    status: str

def extract_matched_terms(query: str, resume_text: str) -> List[str]:
    """Extract terms from query that appear in resume text."""
    query_terms = re.findall(r'\b\w+\b', query.lower())
    resume_lower = resume_text.lower()
    
    matched = []
    for term in query_terms:
        if len(term) > 2 and term in resume_lower:
            matched.append(term)
    
    return list(set(matched))

def generate_snippet(resume_text: str, matched_terms: List[str], max_length: int = 150) -> str:
    """Generate a snippet highlighting matched terms."""
    if not matched_terms:
        return resume_text[:max_length] + "..." if len(resume_text) > max_length else resume_text
    
    # Find the best sentence containing matched terms
    sentences = re.split(r'[.!?]+', resume_text)
    best_sentence = ""
    max_matches = 0
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        matches = sum(1 for term in matched_terms if term in sentence_lower)
        if matches > max_matches:
            max_matches = matches
            best_sentence = sentence.strip()
    
    if best_sentence:
        if len(best_sentence) > max_length:
            return best_sentence[:max_length] + "..."
        return best_sentence
    
    return resume_text[:max_length] + "..." if len(resume_text) > max_length else resume_text

def get_all_active_candidates() -> List[dict]:
    """Fetch all active candidates from Airtable."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_CANDIDATES}"
    params = {"filterByFormula": "NOT({Status} = 'Rejected')"}
    
    all_records = []
    offset = None
    
    while True:
        if offset:
            params["offset"] = offset
        
        response = requests.get(url, headers=AIRTABLE_HEADERS, params=params)
        if response.status_code != 200:
            break
            
        data = response.json()
        all_records.extend(data.get("records", []))
        
        offset = data.get("offset")
        if not offset:
            break
    
    return all_records

@app.get("/")
async def root():
    return {"message": "Signal API", "version": "1.0.0"}

@app.post("/api/search", response_model=List[CandidateResult])
async def search_candidates(request: SearchRequest):
    """Search and rank candidates using natural language query."""
    try:
        # Fetch all active candidates
        candidates = get_all_active_candidates()
        
        results = []
        for candidate in candidates:
            fields = candidate.get("fields", {})
            
            # Get stored scores with defaults
            final_score = fields.get("Final Score", 0.5)
            fit_score = fields.get("Fit Score", 0.5)
            intent_count = fields.get("Intent Count", 1)
            
            # Extract matched terms and calculate simple relevance
            resume_text = fields.get("Resume Text", "")
            matched_terms = extract_matched_terms(request.query, resume_text)
            
            # Simple relevance calculation based on term matches and stored scores
            term_match_score = min(len(matched_terms) * 0.2, 1.0)
            relevance = 0.4 * term_match_score + 0.6 * final_score
            
            # Generate snippet
            snippet = generate_snippet(resume_text, matched_terms)
            
            result = CandidateResult(
                candidate_id=fields.get("Candidate Name", ""),
                name=fields.get("Candidate Name", ""),
                relevance=round(relevance, 3),
                fit_score=round(fit_score, 3),
                intent_count=intent_count,
                matched_terms=matched_terms,
                snippet=snippet,
                shortlisted=fields.get("Shortlisted", False),
                status=fields.get("Status", "Active")
            )
            
            results.append(result)
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x.relevance, reverse=True)
        return results[:request.limit]
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/candidate/{candidate_id}")
async def get_candidate_details(candidate_id: str):
    """Get detailed candidate information."""
    try:
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_CANDIDATES}"
        params = {"filterByFormula": f"{{Candidate Name}} = '{candidate_id}'"}
        
        response = requests.get(url, headers=AIRTABLE_HEADERS, params=params)
        if response.status_code == 200:
            records = response.json().get("records", [])
            if records:
                return {
                    "success": True,
                    "candidate": records[0]
                }
        
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    except Exception as e:
        print(f"Get candidate error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
