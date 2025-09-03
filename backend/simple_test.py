#!/usr/bin/env python3
"""
Simple test to add a candidate directly to your existing Airtable structure
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY") or os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_CANDIDATES = os.getenv("AIRTABLE_TABLE_CANDIDATES", "Candidates")

# Test adding a candidate with your existing field structure
url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_CANDIDATES}"
headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# Create a test candidate using your existing field names
test_candidate = {
    "fields": {
        "Candidate Name": "Sarah Chen",
        "Email Address": "sarah.chen@email.com",
        "Resume Text": "Senior Data Analyst with 4 years of experience in business intelligence and data visualization. Expertise in Power BI, SQL, Python, and Excel for creating comprehensive dashboards and reports.",
        "Candidate ID": "C-001",
        "Role Title": "Senior Data Analyst",
        "Role Family": "Analyst"
    }
}

print("Adding test candidate...")
response = requests.post(url, headers=headers, json=test_candidate)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("✅ Successfully added candidate!")
else:
    print("❌ Failed to add candidate")
    print("Available fields in your table might be different.")
    
    # Let's check what fields are available
    print("\nChecking existing records to see field structure...")
    get_response = requests.get(url, headers=headers)
    if get_response.status_code == 200:
        records = get_response.json().get("records", [])
        if records:
            print("Available fields:")
            for field_name in records[0].get("fields", {}).keys():
                print(f"  - {field_name}")
        else:
            print("No existing records found.")
