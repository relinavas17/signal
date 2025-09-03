from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import json
import numpy as np
from datetime import datetime
import requests
import openai
from sklearn.metrics.pairwise import cosine_similarity
import re
from urllib.parse import quote
# Try to import agents module, but make it optional
try:
    from agents import analyze_candidate_fit
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    def analyze_candidate_fit(*args, **kwargs):
        return None

load_dotenv()

app = FastAPI(title="Signal API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
    ],
    allow_origin_regex=r"^http://127\\.0\\.0\\.1:\\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY") or os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_CANDIDATES = os.getenv("AIRTABLE_TABLE_CANDIDATES", "Candidates")
AIRTABLE_TABLE_APPLICATIONS = os.getenv("AIRTABLE_TABLE_APPLICATIONS", "Applications")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "20"))
INTENT_CAP = int(os.getenv("INTENT_CAP", "5"))
RELEVANCE_ALPHA = float(os.getenv("RELEVANCE_ALPHA", "0.6"))
FINAL_SCORE_WEIGHT = float(os.getenv("FINAL_SCORE_WEIGHT", "0.4"))

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Airtable headers
AIRTABLE_HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# Debug: Print configuration (remove in production)
print(f"AIRTABLE_API_KEY configured: {'Yes' if AIRTABLE_API_KEY else 'No'}")
print(f"AIRTABLE_BASE_ID: {AIRTABLE_BASE_ID}")
print(f"OPENAI_API_KEY configured: {'Yes' if OPENAI_API_KEY else 'No'}")

# Pydantic models
class IngestApplicationRequest(BaseModel):
    candidate_id: str
    name: str
    email: str
    resume_url: Optional[str] = None
    resume_text: Optional[str] = None
    role_title: str
    role_family: str
    applied_at: str

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 20

class ShortlistRequest(BaseModel):
    candidate_id: str
    shortlisted: bool

class RejectRequest(BaseModel):
    candidate_id: str

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
    # Additional fields for UI rendering
    email: Optional[str] = None
    resume_url: Optional[str] = None
    resume_text: Optional[str] = None
    summary: Optional[str] = None
    resume_photo_url: Optional[str] = None

class UICandidate(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    summary: Optional[str] = None
    resumeUrl: Optional[str] = None

# Utility functions
def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using OpenAI. Returns empty list if API fails."""
    try:
        response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return empty list to trigger fallback search
        return []

def cosine_sim(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
    
    vec1_np = np.array(vec1).reshape(1, -1)
    vec2_np = np.array(vec2).reshape(1, -1)
    
    return cosine_similarity(vec1_np, vec2_np)[0][0]

def calculate_text_similarity(query: str, text: str) -> float:
    """Calculate text similarity using keyword matching as fallback."""
    if not query or not text:
        return 0.0
    
    # Coerce non-string text to string
    if not isinstance(text, str):
        try:
            text = json.dumps(text)
        except Exception:
            text = str(text)
    
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(query_words.intersection(text_words))
    union = len(query_words.union(text_words))
    
    if union == 0:
        return 0.0
    
    return intersection / union

def extract_matched_terms(query: str, resume_text: str) -> List[str]:
    """Extract terms from query that appear in resume text."""
    query_terms = re.findall(r'\b\w+\b', query.lower())
    # Coerce non-string resume_text to string
    if not isinstance(resume_text, str):
        try:
            resume_text = json.dumps(resume_text)
        except Exception:
            resume_text = str(resume_text)
    resume_lower = resume_text.lower()
    
    matched = []
    for term in query_terms:
        if len(term) > 2 and term in resume_lower:
            matched.append(term)
    
    return list(set(matched))

def calculate_term_boost(matched_terms: List[str]) -> float:
    """Calculate boost score based on matched terms."""
    return min(len(matched_terms) * 0.05, 0.1)

def generate_snippet(resume_text: str, matched_terms: List[str], max_length: int = 150) -> str:
    """Generate a snippet highlighting matched terms."""
    # Coerce non-string resume_text to string
    if not isinstance(resume_text, str):
        try:
            resume_text = json.dumps(resume_text)
        except Exception:
            resume_text = str(resume_text)
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

# ---- Lightweight keyword utilities for UI search ----
STOPWORDS = set(
    [
        "a","an","the","and","or","but","if","then","else","for","to","of","in","on","at","by","with","from",
        "is","are","was","were","be","been","being","as","it","this","that","these","those","you","your","yours",
        "i","we","they","he","she","them","him","her","my","our","us","me"
    ]
)

def tokenize_query(query: str) -> List[str]:
    if not query:
        return []
    tokens = re.split(r"[^a-z0-9]+", query.lower())
    terms = []
    seen = set()
    for t in tokens:
        if not t or len(t) < 2 or t in STOPWORDS:
            continue
        if t not in seen:
            seen.add(t)
            terms.append(t)
    return terms

def extract_phrases(query: str) -> List[str]:
    if not query:
        return []
    return re.findall(r'"([^"]+)"', query.lower())

# Airtable operations
def get_candidate_by_id(candidate_id: str) -> Optional[dict]:
    """Fetch candidate from Airtable by ID."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_CANDIDATES}"
    params = {"filterByFormula": f"{{Candidate Name}} = '{candidate_id}'"}
    
    response = requests.get(url, headers=AIRTABLE_HEADERS, params=params)
    if response.status_code == 200:
        records = response.json().get("records", [])
        return records[0] if records else None
    return None

def upsert_candidate(candidate_data: dict) -> dict:
    """Create or update candidate in Airtable."""
    existing = get_candidate_by_id(candidate_data["Candidate Name"])
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_CANDIDATES}"
    
    if existing:
        # Update existing record
        record_id = existing["id"]
        url = f"{url}/{record_id}"
        response = requests.patch(url, headers=AIRTABLE_HEADERS, json={"fields": candidate_data})
    else:
        # Create new record
        response = requests.post(url, headers=AIRTABLE_HEADERS, json={"fields": candidate_data})
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail=f"Failed to upsert candidate: {response.text}")

def create_application(application_data: dict) -> dict:
    """Create application record in Airtable."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_APPLICATIONS}"
    
    response = requests.post(url, headers=AIRTABLE_HEADERS, json={"fields": application_data})
    
    if response.status_code == 201:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail=f"Failed to create application: {response.text}")

def get_applications_count(candidate_name: str) -> int:
    """Get count of applications for a candidate."""
    # For now, return 1 since we're using the simplified approach
    # In a full implementation, you'd query the Applications table
    return 1

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

def update_candidate_field(candidate_id: str, field_updates: dict) -> dict:
    """Update specific fields for a candidate."""
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_CANDIDATES}/{candidate['id']}"
    response = requests.patch(url, headers=AIRTABLE_HEADERS, json={"fields": field_updates})
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail=f"Failed to update candidate: {response.text}")

# API endpoints
@app.get("/")
async def root():
    return {"message": "Zenafide HR AI API", "version": "1.0.0"}

@app.post("/api/ingest_application")
async def ingest_application(request: IngestApplicationRequest):
    """Ingest a new application and update candidate scores."""
    try:
        # Prepare candidate data using your Airtable field names
        candidate_data = {
            "Candidate Name": request.name,
            "Email Address": request.email,
            "Status": "Active"
        }
        
        if request.resume_url:
            candidate_data["resume_url"] = request.resume_url
        
        if request.resume_text:
            candidate_data["Resume Text"] = request.resume_text
            
            # Generate embedding if resume text is provided
            embedding = get_embedding(request.resume_text)
            if embedding:
                candidate_data["Resume Embedding"] = json.dumps(embedding)
        
        # Update intent count
        intent_count = get_applications_count(request.name) + 1
        candidate_data["Intent Count"] = intent_count
        
        # Calculate scores
        intent_norm = min(intent_count / INTENT_CAP, 1.0)
        fit_score = 0.5  # Default fit score, can be improved with query-specific calculation
        final_score = 0.5 * intent_norm + 0.5 * fit_score
        
        candidate_data["Fit Score"] = fit_score
        candidate_data["Final Score"] = final_score
        
        # Generate AI fit explanation if enabled
        if request.resume_text:
            fit_explanation = analyze_candidate_fit(
                request.resume_text, 
                f"{request.role_title} in {request.role_family}", 
                request.name
            )
            if fit_explanation:
                candidate_data["Fit Explanation"] = fit_explanation
        
        # Upsert candidate
        candidate_record = upsert_candidate(candidate_data)
        
        # Create application record
        application_data = {
            "candidate_id": request.candidate_id,
            "role_title": request.role_title,
            "role_family": request.role_family,
            "applied_at": request.applied_at
        }
        
        application_record = create_application(application_data)
        
        return {
            "success": True,
            "candidate": candidate_record,
            "application": application_record
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_candidates_ui(query: str = ""):
    """GET search that fetches Candidates from Airtable and ranks by relevancy (Summary) + intent.
    Returns minimal fields for UI cards.
    """
    try:
        # Build Airtable URL
        base_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{quote(AIRTABLE_TABLE_CANDIDATES)}"
        # Avoid specifying fields[] because unknown field names cause 422 errors
        params: List[tuple] = [("pageSize", 100)]

        all_records: List[dict] = []
        fetched = 0
        offset = None
        print(f"[GET /api/search] Fetching from Airtable table='{AIRTABLE_TABLE_CANDIDATES}' base='{AIRTABLE_BASE_ID}'")
        while True and fetched < 200:
            local_params = list(params)
            if offset:
                local_params.append(("offset", offset))
            resp = requests.get(base_url, headers=AIRTABLE_HEADERS, params=local_params)
            print(f"[GET /api/search] Airtable status={resp.status_code}")
            if resp.status_code != 200:
                try:
                    print(f"[GET /api/search] Airtable error body: {resp.text[:500]}")
                except Exception:
                    pass
                break
            data = resp.json()
            recs = data.get("records", [])
            all_records.extend(recs)
            fetched += len(recs)
            offset = data.get("offset")
            if not offset:
                break
        print(f"[GET /api/search] Total records fetched: {len(all_records)}")

        # Prepare search terms and phrases
        terms = tokenize_query(query)
        phrases = extract_phrases(query)

        def get_intent_raw(f: dict) -> float:
            for k in ("Intent Score", "Intent Count", "intent_count"):
                val = f.get(k)
                if isinstance(val, (int, float)):
                    return float(val)
                # Airtable sometimes returns numeric-like strings
                try:
                    return float(val)
                except Exception:
                    pass
            return 0.0

        items = []
        for rec in all_records:
            f = rec.get("fields", {})
            name = f.get("Candidate Name") or f.get("Name") or ""
            email = f.get("Email Address") or None
            # Prefer 'Candidate Summary' (your column), with sensible fallbacks
            summary = (
                f.get("Candidate Summary")
                or f.get("Summary")
                or f.get("Profile Summary")
                or f.get("About")
                or f.get("Overview")
                or None
            )
            # Normalize summary to a plain string
            if summary is not None and not isinstance(summary, str):
                # If Airtable returns a rich object, extract a likely text field
                if isinstance(summary, dict):
                    for key in ("value", "text", "content"):
                        v = summary.get(key)
                        if isinstance(v, str) and v.strip():
                            summary = v
                            break
                    else:
                        # Fallback to string form
                        try:
                            summary = json.dumps(summary)
                        except Exception:
                            summary = str(summary)
                elif isinstance(summary, list):
                    # Join list of strings/dicts into text
                    parts = []
                    for it in summary:
                        if isinstance(it, str):
                            parts.append(it)
                        elif isinstance(it, dict):
                            for key in ("value", "text", "content"):
                                v = it.get(key)
                                if isinstance(v, str) and v.strip():
                                    parts.append(v)
                                    break
                    summary = " \n".join(parts) if parts else str(summary)
                else:
                    summary = str(summary)
            resumeUrl = None
            att = f.get("Resume")
            if isinstance(att, list) and att:
                first = att[0]
                if isinstance(first, dict):
                    resumeUrl = first.get("url") or None

            # Compute relevancy from Summary (safe for non-string via coercion above)
            text = (summary or "").lower()
            hits = sum(1 for t in terms if t in text)
            relevancy = (hits / len(terms)) if terms else 0.0
            # Optional phrase boost: +0.1 per phrase (max +0.3)
            boost = 0.0
            for ph in phrases:
                if ph and ph in text:
                    boost += 0.1
            relevancy = min(1.0, relevancy + min(boost, 0.3))

            intent_raw = get_intent_raw(f)
            intent_norm = min((intent_raw or 0.0) / 5.0, 1.0)

            if terms:
                final_score = 0.6 * relevancy + 0.4 * intent_norm
            else:
                # Empty query: rank by intent only
                final_score = intent_norm

            items.append(
                {
                    "id": rec.get("id", ""),
                    "name": name or "",
                    "email": email,
                    "summary": summary,
                    "resumeUrl": resumeUrl,
                    "relevance": round(relevancy, 3),
                    "intentCount": int(intent_raw),
                    "_finalScore": final_score,
                }
            )

        items.sort(key=lambda x: x.get("_finalScore", 0.0), reverse=True)
        # Strip internal field
        for it in items:
            it.pop("_finalScore", None)
        return items

    except Exception as e:
        print(f"GET /api/search error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=List[CandidateResult])
async def search_candidates(request: SearchRequest):
    """Search candidates by keyword similarity against Resume Text and Intent Count."""
    try:
        # Fetch all active candidates
        candidates = get_all_active_candidates()

        results = []
        for candidate in candidates:
            print("candidate", candidate)
            fields = candidate.get("fields", {})
            resume_text = fields.get("Resume Text", "")
            # Coerce non-string resume_text to string for downstream processing
            if not isinstance(resume_text, str):
                try:
                    resume_text = json.dumps(resume_text)
                except Exception:
                    resume_text = str(resume_text)

            # Keyword-based text similarity
            text_sim = calculate_text_similarity(request.query, resume_text)

            # Intent normalization from Airtable Intent Count
            intent_count = int(fields.get("Intent Count", 0) or 0)
            intent_norm = min(intent_count / INTENT_CAP, 1.0)

            # Relevance = weighted combo of text similarity and intent
            relevance = RELEVANCE_ALPHA * text_sim + (1.0 - RELEVANCE_ALPHA) * intent_norm

            # Clamp relevance to [0, 1]
            relevance = max(0.0, min(1.0, relevance))

            # Extract matched terms and snippet (display only)
            matched_terms = extract_matched_terms(request.query, resume_text)
            snippet = generate_snippet(resume_text, matched_terms)

            # Email and resume URL extraction for UI
            email = fields.get("Email Address") or fields.get("email") or fields.get("Email")
            resume_url = fields.get("resume_url")
            resume_photo_url = None
            if not resume_url:
                # Try common Airtable attachment fields
                for att_key in ["Resume", "Resume File", "Attachments", "Attachment", "Files"]:
                    att_val = fields.get(att_key)
                    if isinstance(att_val, list) and att_val:
                        first = att_val[0]
                        if isinstance(first, dict) and first.get("url"):
                            resume_url = first.get("url")
                            # Try to extract a thumbnail if available (image or generated)
                            thumbs = first.get("thumbnails") or {}
                            if isinstance(thumbs, dict):
                                # Prefer large then small
                                resume_photo_url = (
                                    (thumbs.get("large") or {}).get("url")
                                    or (thumbs.get("small") or {}).get("url")
                                )
                            break

            # Fallback: if resume_url exists but no thumbnail and attachment includes type image
            if not resume_photo_url:
                for att_key in [
                    "Resume",
                    "Resume File",
                    "Attachments",
                    "Attachment",
                    "Files",
                    "Photos",
                    "Photo",
                    "Resume Photo",
                    "Profile Photo",
                ]:
                    att_val = fields.get(att_key)
                    if isinstance(att_val, list) and att_val:
                        first = att_val[0]
                        if isinstance(first, dict):
                            if first.get("thumbnails"):
                                thumbs = first.get("thumbnails") or {}
                                resume_photo_url = (
                                    (thumbs.get("large") or {}).get("url")
                                    or (thumbs.get("small") or {}).get("url")
                                )
                                break

            # Summary
            summary = (
                fields.get("Candidate Summary")
                or fields.get("Profile Summary")
                or fields.get("About")
                or fields.get("Overview")
            )

            # Use intent_norm as fit_score field for compatibility
            # Determine name and candidate_id from common fields
            name_field = (
                fields.get("Candidate Name")
                or fields.get("Name")
                or fields.get("Full Name")
                or ""
            )
            candidate_identifier = name_field or candidate.get("id", "")
            result = CandidateResult(
                candidate_id=candidate_identifier,
                name=name_field,
                relevance=round(relevance, 3),
                fit_score=round(intent_norm, 3),
                intent_count=intent_count,
                matched_terms=matched_terms,
                snippet=snippet,
                shortlisted=fields.get("Shortlisted", False),
                status=fields.get("Status", "Active"),
                email=email,
                resume_url=resume_url,
                resume_text=resume_text,
                summary=summary,
                resume_photo_url=resume_photo_url,
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

@app.post("/api/shortlist")
async def shortlist_candidate(request: ShortlistRequest):
    """Toggle candidate shortlist status."""
    try:
        updated_candidate = update_candidate_field(
            request.candidate_id,
            {"Shortlisted": request.shortlisted}
        )
        
        return {
            "success": True,
            "candidate": updated_candidate
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reject")
async def reject_candidate(request: RejectRequest):
    """Reject a candidate."""
    try:
        updated_candidate = update_candidate_field(
            request.candidate_id,
            {"Status": "Rejected"}
        )
        
        return {
            "success": True,
            "candidate": updated_candidate
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/candidate/{candidate_id}")
async def get_candidate_details(candidate_id: str):
    """Get detailed candidate information."""
    try:
        candidate = get_candidate_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return {
            "success": True,
            "candidate": candidate
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
