import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import jobs_collection
from ai.skill_extractor import extract_skills_batch

load_dotenv()

ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY')

def fetch_adzuna_jobs(what='developer', results_per_page=20, where='india'):
    print(f"Fetching Adzuna jobs for: {what}")
    
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'results_per_page': results_per_page,
        'what': what,
        'where': where,
        'max_days_old': 30,
        'category': 'it-jobs'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('results', []):
                jobs.append({
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company', {}).get('display_name', 'N/A'),
                    'location': job.get('location', {}).get('display_name', 'N/A'),
                    'description': job.get('description', 'N/A'),
                    'posted_date': job.get('created'),
                    'source': 'Adzuna',
                    'jobUrl': job.get('redirect_url'),
                    'scrapedAt': datetime.now(),
                    'skills': []
                })
            
            print(f"   Got {len(jobs)} jobs")
            return jobs
        
        else:
            print(f"Error: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"Error: {e}")
        return []


def save_jobs_to_db(jobs):
    """Save jobs to MongoDB"""
    if not jobs:
        print("No jobs to save")
        return 0
    
    try:
        result = jobs_collection.insert_many(jobs)
        print(f"Saved {len(result.inserted_ids)} jobs to database")
        return len(result.inserted_ids)
    except Exception as e:
        print(f"Error saving to database: {e}")
        return 0


if __name__ == "__main__":
    print("=" * 70)
    print("ADZUNA JOB COLLECTOR WITH AI SKILL EXTRACTION - DAY 3")
    print("=" * 70)
    
    # Step 1: Fetch jobs
    jobs = fetch_adzuna_jobs()
    
    if jobs:
        # Step 2: Extract skills using AI
        print("\n" + "=" * 70)
        jobs_with_skills = extract_skills_batch(jobs)
        
        # Step 3: Save to database
        print("\n" + "=" * 70)
        saved_count = save_jobs_to_db(jobs_with_skills)
        
        # Step 4: Show summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Jobs Fetched: {len(jobs)}")
        print(f"AI Processed: {len(jobs_with_skills)}")
        print(f"Jobs Saved: {saved_count}")
        print(f"Source: Adzuna API")
        print(f"Timestamp: {datetime.now()}")
        
        # Show samples
        print("\nSample Jobs with Extracted Skills:")
        for i, job in enumerate(jobs_with_skills[:3], 1):
            print(f"\n{i}. {job['title']} @ {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Skills ({len(job['skills'])}): {', '.join(job['skills'][:10])}")
            if len(job['skills']) > 10:
                print(f"   ... and {len(job['skills']) - 10} more")
    else:
        print("\nFailed to fetch jobs.")
        print("\nTIP: Try testing the API directly in your browser:")
        print(f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&results_per_page=5&what=developer&where=india")