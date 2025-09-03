#!/usr/bin/env python3
"""
Test the search API directly
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

# Test search
search_data = {
    "query": "data analyst Power BI",
    "limit": 5
}

print("Testing search API...")
try:
    response = requests.post(
        f"{API_BASE_URL}/api/search",
        json=search_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"\n✅ Search successful! Found {len(results)} candidates")
        for result in results:
            print(f"  - {result['name']} (Relevance: {result['relevance']})")
    else:
        print("❌ Search failed")
        
except Exception as e:
    print(f"Error: {e}")
