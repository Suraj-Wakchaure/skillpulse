"""
Master Job Collector
Orchestrates collection from all API sources
"""

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(__file__))

# FIXED IMPORTS - match your actual function names
from collectors.adzuna_collector import fetch_adzuna_jobs
from collectors.remotive_collector import collect_remotive_jobs
from collectors.jsearch_collector import collect_jsearch_jobs
from ai.skill_extractor import extract_skills_batch
from database import jobs_collection, collection_logs_collection

def deduplicate_jobs(jobs):
    """
    Remove duplicates across all sources
    Uses (title.lower(), company.lower()) as key
    """
    seen = set()
    unique_jobs = []
    
    for job in jobs:
        key = (job['title'].lower().strip(), job['company'].lower().strip())
        
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    duplicates_removed = len(jobs) - len(unique_jobs)
    
    if duplicates_removed > 0:
        print(f"\n🔄 Deduplication: Removed {duplicates_removed} duplicates")
    
    return unique_jobs


def save_jobs_batch(jobs):
    """Save jobs to database with global deduplication"""
    
    if not jobs:
        return 0
    
    saved = 0
    duplicates = 0
    
    for job in jobs:
        # Check if job already exists in database (any source)
        existing = jobs_collection.find_one({
            'title': job['title'],
            'company': job['company']
        })
        
        if existing:
            duplicates += 1
        else:
            jobs_collection.insert_one(job)
            saved += 1
    
    print(f"   💾 Saved to DB: {saved} | Already existed: {duplicates}")
    return saved


def collect_all_jobs():
    """
    Main collection orchestrator
    Collects from all sources, deduplicates, extracts skills
    """
    
    print("=" * 70)
    print("SKILLPULSE - MULTI-SOURCE JOB COLLECTION")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sources = {}
    all_jobs = []
    
    # 1. Collect from Adzuna
    print("\n" + "=" * 70)
    adzuna_jobs = fetch_adzuna_jobs()  # FIXED: use fetch_adzuna_jobs
    sources['adzuna'] = len(adzuna_jobs)
    all_jobs.extend(adzuna_jobs)
    
    # 2. Collect from Remotive
    print("\n" + "=" * 70)
    remotive_jobs = collect_remotive_jobs(limit=100)
    sources['remotive'] = len(remotive_jobs)
    all_jobs.extend(remotive_jobs)
    
    # 3. Collect from JSearch
    print("\n" + "=" * 70)
    jsearch_queries = [
        'Python developer India',
        'JavaScript developer India',
        'React developer India',
        'Java developer India',
        'Full stack developer India'
    ]
    jsearch_jobs = collect_jsearch_jobs(queries=jsearch_queries, max_per_query=10)
    sources['jsearch'] = len(jsearch_jobs)
    all_jobs.extend(jsearch_jobs)
    
    # Statistics
    print("\n" + "=" * 70)
    print("📊 COLLECTION SUMMARY")
    print("=" * 70)
    print(f"Adzuna:   {sources['adzuna']} jobs")
    print(f"Remotive: {sources['remotive']} jobs")
    print(f"JSearch:  {sources['jsearch']} jobs")
    print(f"Total fetched: {len(all_jobs)} jobs")
    
    # Deduplicate across sources
    unique_jobs = deduplicate_jobs(all_jobs)
    print(f"After deduplication: {len(unique_jobs)} unique jobs")
    
    # Save to database
    print("\n💾 Saving to database...")
    saved = save_jobs_batch(unique_jobs)
    
    # AI Skill Extraction
    if saved > 0:
        print("\n" + "=" * 70)
        print("🤖 EXTRACTING SKILLS WITH AI")
        print("=" * 70)
        
        # Get jobs without skills (empty array or doesn't exist)
        jobs_without_skills = list(jobs_collection.find({
            '$or': [
                {'skills': {'$exists': False}},
                {'skills': []}
            ]
        }).limit(saved))
        
        if jobs_without_skills:
            print(f"Found {len(jobs_without_skills)} jobs needing skill extraction")
            
            # Extract skills
            jobs_with_skills = extract_skills_batch(jobs_without_skills)
            
            # Update database
            updated = 0
            for job in jobs_with_skills:
                jobs_collection.update_one(
                    {'_id': job['_id']},
                    {'$set': {'skills': job['skills']}}
                )
                updated += 1
            
            print(f"✅ Updated {updated} jobs with extracted skills")
    
    # Log collection
    log_entry = {
        'timestamp': datetime.now(),
        'totalFetched': len(all_jobs),
        'afterDedup': len(unique_jobs),
        'saved': saved,
        'sources': sources,
        'status': 'success'
    }
    collection_logs_collection.insert_one(log_entry)
    
    print("\n" + "=" * 70)
    print("✅ COLLECTION COMPLETE")
    print("=" * 70)
    print(f"New jobs added: {saved}")
    print(f"Total jobs in database: {jobs_collection.count_documents({})}")
    print("=" * 70)


if __name__ == "__main__":
    collect_all_jobs()