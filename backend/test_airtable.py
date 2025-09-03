#!/usr/bin/env python3
"""
Test Airtable connection
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY") or os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_CANDIDATES = os.getenv("AIRTABLE_TABLE_CANDIDATES", "Candidates")

print(f"API Key: {AIRTABLE_API_KEY[:20]}..." if AIRTABLE_API_KEY else "No API Key")
print(f"Base ID: {AIRTABLE_BASE_ID}")
print(f"Table: {AIRTABLE_TABLE_CANDIDATES}")

# Test connection
url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_CANDIDATES}"
headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

print(f"\nTesting connection to: {url}")

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code != 200:
    print("\n❌ Airtable connection failed!")
    print("Please check:")
    print("1. Your Airtable Personal Access Token is correct")
    print("2. Your Base ID is correct") 
    print("3. The 'Candidates' table exists in your base")
    print("4. Your token has read/write permissions")
else:
    print("\n✅ Airtable connection successful!")
