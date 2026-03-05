import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import jobs_collection

def view_latest_jobs(limit=10):
    """View latest collected jobs"""
    print("=" * 70)
    print("LATEST COLLECTED JOBS")
    print("=" * 70)
    
    # Get jobs sorted by scraped_at (newest first)
    jobs = jobs_collection.find().sort('scraped_at', -1).limit(limit)
    
    count = 0
    for job in jobs:
        count += 1
        print(f"\n{count}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Source: {job['source']}")
        print(f"   Collected: {job['scraped_at']}")
        print(f"   Description: {job['description'][:150]}...")
    
    # Show total count
    total = jobs_collection.count_documents({})
    print("\n" + "=" * 70)
    print(f"Showing {count} of {total} total jobs in database")
    print("=" * 70)

if __name__ == "__main__":
    view_latest_jobs(10)