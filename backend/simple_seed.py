#!/usr/bin/env python3
"""
Simple seed script that works with your existing Airtable structure
"""

import os
import requests
import json
from dotenv import load_dotenv
import openai

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY") or os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def get_embedding(text):
    """Generate embedding for text using OpenAI."""
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

# Sample candidates
candidates = [
    {
        "Candidate Name": "Sarah Chen",
        "Email Address": "sarah.chen@email.com",
        "Resume Text": "Senior Data Analyst with 4 years of experience in business intelligence and data visualization. Expertise in Power BI, SQL, Python, and Excel for creating comprehensive dashboards and reports. Led cross-functional teams to deliver data-driven insights that increased revenue by 15%. Strong background in statistical analysis, data modeling, and ETL processes.",
        "Status": "Active",
        "Intent Count": 3,
        "Fit Score": 0.85,
        "Final Score": 0.75
    },
    {
        "Candidate Name": "Michael Rodriguez", 
        "Email Address": "m.rodriguez@email.com",
        "Resume Text": "Full Stack Developer with 5 years of experience building scalable web applications. Proficient in React, TypeScript, Node.js, and Python. Experience with AWS, Docker, and Kubernetes. Built and maintained microservices architecture serving 100k+ daily active users. Strong knowledge of database design (PostgreSQL, MongoDB) and API development.",
        "Status": "Active",
        "Intent Count": 2,
        "Fit Score": 0.70,
        "Final Score": 0.60
    },
    {
        "Candidate Name": "Emily Johnson",
        "Email Address": "emily.j@email.com",
        "Resume Text": "Marketing Manager with 6 years in digital marketing and campaign management. Expert in Google Analytics, Facebook Ads, LinkedIn advertising, and marketing automation. Managed $2M annual marketing budget and increased lead generation by 40%. Strong background in content marketing, SEO, and conversion optimization.",
        "Status": "Active", 
        "Intent Count": 1,
        "Fit Score": 0.60,
        "Final Score": 0.50
    },
    {
        "Candidate Name": "David Kim",
        "Email Address": "david.kim@email.com",
        "Resume Text": "Data Engineer with 3 years of experience in big data processing and analytics infrastructure. Expertise in Python, SQL, Apache Spark, and Airflow for building ETL pipelines. Experience with AWS services (S3, Redshift, EMR) and real-time data streaming. Built data warehouses processing 10TB+ daily data volumes.",
        "Status": "Active",
        "Intent Count": 5,
        "Fit Score": 0.90,
        "Final Score": 0.95
    }
]

def add_candidates():
    """Add candidates to Airtable with embeddings"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Candidates"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for candidate in candidates:
        print(f"Adding {candidate['Candidate Name']}...")
        
        # Generate embedding
        embedding = get_embedding(candidate["Resume Text"])
        if embedding:
            candidate["Resume Embedding"] = json.dumps(embedding)
        
        # Add candidate
        response = requests.post(url, headers=headers, json={"fields": candidate})
        
        if response.status_code == 200:
            print(f"✅ Added {candidate['Candidate Name']}")
        else:
            print(f"❌ Failed to add {candidate['Candidate Name']}: {response.text}")

if __name__ == "__main__":
    print("Adding sample candidates to Airtable...")
    add_candidates()
    print("\nDone! You can now test the search functionality.")
