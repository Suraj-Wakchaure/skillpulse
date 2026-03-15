"""
Remotive API Job Collector
Fetches remote software development jobs
"""

import requests
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import jobs_collection

def collect_remotive_jobs(limit=100):
    """
    Collect jobs from Remotive API
    
    Args:
        limit: Maximum number of jobs to fetch
    
    Returns:
        List of job dictionaries
    """
    
    print("🌍 Collecting jobs from Remotive API...")
    
    jobs = []
    categories = ['software-dev']
    
    try:
        for category in categories:
            response = requests.get(
                "https://remotive.com/api/remote-jobs",
                params={
                    "category": category,
                    "limit": limit
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                api_jobs = data.get('jobs', [])
                
                print(f"   Fetched {len(api_jobs)} jobs from category: {category}")
                
                for job in api_jobs:
                    parsed_job = {
                        'title': job.get('title', 'N/A'),
                        'company': job.get('company_name', 'N/A'),
                        'location': 'Remote',
                        'description': job.get('description', 'N/A'),
                        'experience': None,
                        'posted_date': job.get('publication_date'),
                        'source': 'Remotive',
                        'jobUrl': job.get('url', 'N/A'),
                        'skills': [],
                        'scrapedAt': datetime.now()
                    }
                    
                    jobs.append(parsed_job)
            else:
                print(f"   ⚠️  Error {response.status_code} for category: {category}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return jobs


def save_remotive_jobs(jobs):
    """Save jobs to database with deduplication"""
    
    if not jobs:
        print("   No jobs to save")
        return 0
    
    saved = 0
    duplicates = 0
    
    for job in jobs:
        existing = jobs_collection.find_one({
            'title': job['title'],
            'company': job['company'],
            'source': 'Remotive'
        })
        
        if existing:
            duplicates += 1
        else:
            jobs_collection.insert_one(job)
            saved += 1
    
    print(f"   ✅ Saved: {saved} | Duplicates: {duplicates}")
    return saved


if __name__ == "__main__":
    print("=" * 70)
    print("REMOTIVE JOB COLLECTOR")
    print("=" * 70)
    
    jobs = collect_remotive_jobs(limit=100)
    print(f"\nTotal jobs collected: {len(jobs)}")
    
    if jobs:
        saved = save_remotive_jobs(jobs)
        print(f"\n✅ Collection complete! {saved} new jobs added")
    
    print("=" * 70)