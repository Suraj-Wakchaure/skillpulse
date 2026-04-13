"""
JSearch API Job Collector (RapidAPI)
Fetches aggregated job listings
"""

import requests
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import jobs_collection
from dotenv import load_dotenv

load_dotenv()

def collect_jsearch_jobs(queries=['Python developer India', 'JavaScript developer India'], max_per_query=10):
    """
    Collect jobs from JSearch API
    
    Args:
        queries: List of search queries
        max_per_query: Max results per query
    
    Returns:
        List of job dictionaries
    """
    
    print("Collecting jobs from JSearch API...")
    
    api_key = os.getenv('JSEARCH_API_KEY')
    
    if not api_key:
        print("No JSearch API key found in .env")
        return []
    
    jobs = []
    
    for query in queries:
        try:
            response = requests.get(
                "https://jsearch.p.rapidapi.com/search",
                headers={
                    "X-RapidAPI-Key": api_key,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
                },
                params={
                    "query": query,
                    "page": "1",
                    "num_pages": "1",
                    "date_posted": "month"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                api_jobs = data.get('data', [])[:max_per_query]
                
                print(f"   Fetched {len(api_jobs)} jobs for query: {query}")
                
                for job in api_jobs:
                    parsed_job = {
                        'title': job.get('job_title', 'N/A'),
                        'company': job.get('employer_name', 'N/A'),
                        'location': job.get('job_city', 'India'),
                        'description': job.get('job_description', 'N/A'),
                        'experience': job.get('job_required_experience', {}).get('required_experience_in_months'),
                        'posted_date': job.get('job_posted_at_datetime_utc'),
                        'source': 'JSearch',
                        'jobUrl': job.get('job_apply_link', 'N/A'),
                        'skills': [],
                        'scrapedAt': datetime.now()
                    }
                    
                    jobs.append(parsed_job)
            else:
                print(f"Error {response.status_code} for query: {query}")
        
        except Exception as e:
            print(f"Error for query '{query}': {e}")
    
    return jobs


def save_jsearch_jobs(jobs):
    """Save jobs to database with deduplication"""
    
    if not jobs:
        print("No jobs to save")
        return 0
    
    saved = 0
    duplicates = 0
    
    for job in jobs:
        existing = jobs_collection.find_one({
            'title': job['title'],
            'company': job['company'],
            'source': 'JSearch'
        })
        
        if existing:
            duplicates += 1
        else:
            jobs_collection.insert_one(job)
            saved += 1
    
    print(f"Saved: {saved} | Duplicates: {duplicates}")
    return saved


if __name__ == "__main__":
    print("=" * 70)
    print("JSEARCH JOB COLLECTOR")
    print("=" * 70)
    
    queries = [
        'Python developer India',
        'JavaScript developer India',
        'React developer India',
        'Full stack developer India'
    ]
    
    jobs = collect_jsearch_jobs(queries=queries, max_per_query=10)
    print(f"\nTotal jobs collected: {len(jobs)}")
    
    if jobs:
        saved = save_jsearch_jobs(jobs)
        print(f"\nCollection complete! {saved} new jobs added")
    
    print("=" * 70)