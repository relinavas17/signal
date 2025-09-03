#!/usr/bin/env python3
"""
Seed data script for Zenafide HR AI Tool
Creates sample candidates with realistic resume data for testing
"""

import requests
import json
from datetime import datetime, timedelta
import random

API_BASE_URL = "http://localhost:8000"

# Sample resume data with different skill sets and experience levels
SAMPLE_CANDIDATES = [
    {
        "candidate_id": "C-001",
        "name": "Sarah Chen",
        "email": "sarah.chen@email.com",
        "resume_text": """
Senior Data Analyst with 4 years of experience in business intelligence and data visualization. 
Expertise in Power BI, SQL, Python, and Excel for creating comprehensive dashboards and reports. 
Led cross-functional teams to deliver data-driven insights that increased revenue by 15%. 
Strong background in statistical analysis, data modeling, and ETL processes. 
Experience with Tableau, R, and machine learning algorithms. 
Proven track record of translating complex data into actionable business recommendations.
        """.strip(),
        "role_title": "Senior Data Analyst",
        "role_family": "Analyst",
        "applications": 3
    },
    {
        "candidate_id": "C-002", 
        "name": "Michael Rodriguez",
        "email": "m.rodriguez@email.com",
        "resume_text": """
Full Stack Developer with 5 years of experience building scalable web applications. 
Proficient in React, TypeScript, Node.js, and Python. Experience with AWS, Docker, and Kubernetes. 
Built and maintained microservices architecture serving 100k+ daily active users. 
Strong knowledge of database design (PostgreSQL, MongoDB) and API development. 
Led frontend development team of 4 engineers. Passionate about clean code and test-driven development.
        """.strip(),
        "role_title": "Senior Full Stack Developer",
        "role_family": "Engineering",
        "applications": 2
    },
    {
        "candidate_id": "C-003",
        "name": "Emily Johnson",
        "email": "emily.j@email.com", 
        "resume_text": """
Marketing Manager with 6 years in digital marketing and campaign management. 
Expert in Google Analytics, Facebook Ads, LinkedIn advertising, and marketing automation. 
Managed $2M annual marketing budget and increased lead generation by 40%. 
Strong background in content marketing, SEO, and conversion optimization. 
Experience with HubSpot, Salesforce, and A/B testing methodologies. 
Led successful product launches and brand awareness campaigns.
        """.strip(),
        "role_title": "Senior Marketing Manager",
        "role_family": "Marketing",
        "applications": 1
    },
    {
        "candidate_id": "C-004",
        "name": "David Kim",
        "email": "david.kim@email.com",
        "resume_text": """
Data Engineer with 3 years of experience in big data processing and analytics infrastructure. 
Expertise in Python, SQL, Apache Spark, and Airflow for building ETL pipelines. 
Experience with AWS services (S3, Redshift, EMR) and real-time data streaming. 
Built data warehouses processing 10TB+ daily data volumes. 
Strong knowledge of data modeling, schema design, and performance optimization. 
Familiar with Kafka, Elasticsearch, and machine learning model deployment.
        """.strip(),
        "role_title": "Data Engineer",
        "role_family": "Engineering", 
        "applications": 5
    },
    {
        "candidate_id": "C-005",
        "name": "Lisa Wang",
        "email": "lisa.wang@email.com",
        "resume_text": """
Business Analyst with 2 years of experience in requirements gathering and process improvement. 
Skilled in data analysis using Excel, SQL, and basic Power BI reporting. 
Collaborated with stakeholders to define business requirements and user stories. 
Experience with Agile methodologies and project management tools like Jira. 
Strong communication skills and ability to bridge technical and business teams. 
Background in finance and operations analysis.
        """.strip(),
        "role_title": "Business Analyst",
        "role_family": "Analyst",
        "applications": 4
    },
    {
        "candidate_id": "C-006",
        "name": "James Thompson",
        "email": "j.thompson@email.com",
        "resume_text": """
DevOps Engineer with 4 years of experience in cloud infrastructure and automation. 
Expert in AWS, Kubernetes, Docker, and Infrastructure as Code (Terraform). 
Built CI/CD pipelines using Jenkins, GitLab CI, and GitHub Actions. 
Experience with monitoring tools like Prometheus, Grafana, and ELK stack. 
Managed production environments serving millions of requests daily. 
Strong background in Linux administration and network security.
        """.strip(),
        "role_title": "DevOps Engineer", 
        "role_family": "Engineering",
        "applications": 2
    }
]

def create_applications():
    """Create sample applications for all candidates"""
    print("Creating sample applications...")
    
    for candidate in SAMPLE_CANDIDATES:
        # Create multiple applications based on the applications count
        for i in range(candidate["applications"]):
            # Vary the application dates
            days_ago = random.randint(1, 90)
            applied_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            application_data = {
                "candidate_id": candidate["candidate_id"],
                "name": candidate["name"],
                "email": candidate["email"],
                "resume_text": candidate["resume_text"],
                "role_title": candidate["role_title"],
                "role_family": candidate["role_family"],
                "applied_at": applied_at
            }
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/ingest_application",
                    json=application_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"✓ Created application for {candidate['name']} (Application {i+1})")
                else:
                    print(f"✗ Failed to create application for {candidate['name']}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"✗ Network error creating application for {candidate['name']}: {e}")

def test_search_queries():
    """Test various search queries to verify the system works"""
    print("\nTesting search queries...")
    
    test_queries = [
        "3 years analyst working with Power BI",
        "Senior data engineer with Python and SQL", 
        "Marketing manager with digital campaign experience",
        "Frontend developer React TypeScript",
        "DevOps engineer AWS Kubernetes"
    ]
    
    for query in test_queries:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/search",
                json={"query": query, "limit": 5},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"✓ Query: '{query}' returned {len(results)} results")
                if results:
                    top_result = results[0]
                    print(f"  Top match: {top_result['name']} (Relevance: {top_result['relevance']:.2f})")
            else:
                print(f"✗ Search failed for '{query}': {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error searching for '{query}': {e}")

def main():
    """Main function to seed the database"""
    print("Zenafide HR AI Tool - Seed Data Script")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code != 200:
            print("✗ API is not running. Please start the backend server first.")
            print("  Run: cd backend && uvicorn app:app --reload")
            return
    except requests.exceptions.RequestException:
        print("✗ Cannot connect to API. Please start the backend server first.")
        print("  Run: cd backend && uvicorn app:app --reload")
        return
    
    print("✓ API is running")
    
    # Create applications
    create_applications()
    
    # Test search functionality
    test_search_queries()
    
    print("\n" + "=" * 50)
    print("Seed data creation completed!")
    print("\nNext steps:")
    print("1. Start the frontend: cd frontend && npm run dev")
    print("2. Open http://localhost:3000")
    print("3. Try searching for candidates using the sample queries above")

if __name__ == "__main__":
    main()
