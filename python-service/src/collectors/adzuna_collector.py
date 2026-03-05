import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import jobs_collection

# Load environment variables
load_dotenv()

# Get API credentials from .env
ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY')

def fetch_adzuna_jobs():
    """
    Fetch jobs from Adzuna API for India tech roles
    """
    print("🔄 Fetching jobs from Adzuna API...")
    
    # API endpoint (India = 'in')
    base_url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    
    # Parameters for our search
    params = {
    'app_id': ADZUNA_APP_ID,
    'app_key': ADZUNA_APP_KEY,
    'results_per_page': 50,
    'what': 'developer',
    'where': 'india',
    'category': 'it-jobs',
    'sort_by': 'date',
    'max_days_old': 14
}
    
    try:
        # Make the API request
        response = requests.get(base_url, params=params, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Extract job data
            jobs = []
            for job in data.get('results', []):
                job_data = {
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company', {}).get('display_name', 'N/A'),
                    'location': job.get('location', {}).get('display_name', 'N/A'),
                    'description': job.get('description', 'N/A'),
                    'posted_date': job.get('created', None),
                    'source': 'Adzuna',
                    'url': job.get('redirect_url', 'N/A'),
                    'scraped_at': datetime.now(),
                    'skills': []  # Will be filled by AI later
                }
                jobs.append(job_data)
            
            print(f"✅ Successfully fetched {len(jobs)} jobs from Adzuna")
            return jobs
        
        else:
            print(f"❌ Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return []
    
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error making API request: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []


def save_jobs_to_db(jobs):
    """Save jobs to MongoDB"""
    if not jobs:
        print("⚠️  No jobs to save")
        return 0
    
    try:
        # Insert jobs into database
        result = jobs_collection.insert_many(jobs)
        print(f"✅ Saved {len(result.inserted_ids)} jobs to database")
        return len(result.inserted_ids)
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        return 0


# Test function
if __name__ == "__main__":
    print("=" * 50)
    print("ADZUNA JOB COLLECTOR - DAY 2 TEST")
    print("=" * 50)
    
    # Step 1: Fetch jobs
    jobs = fetch_adzuna_jobs()
    
    # Step 2: Save to database
    if jobs:
        saved_count = save_jobs_to_db(jobs)
        
        # Step 3: Show summary
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        print(f"Fetched: {len(jobs)} jobs")
        print(f"Saved: {saved_count} jobs")
        print(f"Source: Adzuna API")
        print(f"Timestamp: {datetime.now()}")
        
        # Show sample
        if jobs:
            print(f"\n📝 Sample Job:")
            print(f"  Title: {jobs[0]['title']}")
            print(f"  Company: {jobs[0]['company']}")
            print(f"  Location: {jobs[0]['location']}")
    else:
        print("\n❌ Failed to fetch jobs. Check API keys!")