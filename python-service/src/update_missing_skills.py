import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import jobs_collection
from ai.skill_extractor import extract_skills_from_description
import time

def update_missing_skills():
    """Update jobs that don't have skills extracted yet"""
    
    print("=" * 70)
    print("UPDATING JOBS WITHOUT SKILLS")
    print("=" * 70)
    
    # Find jobs without skills
    jobs_without_skills = list(jobs_collection.find({
        '$or': [
            {'skills': {'$exists': False}},
            {'skills': []},
            {'skills': None}
        ]
    }))
    
    total = len(jobs_without_skills)
    
    if total == 0:
        print("✅ All jobs already have skills!")
        return
    
    print(f"\nFound {total} jobs without skills")
    print("Starting re-extraction with Groq Llama 3.3 70B...")
    print()
    
    updated = 0
    still_empty = 0
    
    for idx, job in enumerate(jobs_without_skills, 1):
        job_id = job['_id']
        description = job.get('description', '')
        
        # Extract skills
        skills = extract_skills_from_description(description)
        
        # Update in database
        jobs_collection.update_one(
            {'_id': job_id},
            {'$set': {'skills': skills}}
        )
        
        if skills:
            updated += 1
            status = f"✓ {len(skills)} skills"
        else:
            still_empty += 1
            status = "✗ no skills"
        
        # Progress
        if idx % 5 == 0 or idx == total:
            print(f"   Progress: {idx}/{total} | Updated: {updated} | Empty: {still_empty}")
        
        # Rate limit
        time.sleep(2)
    
    print()
    print("=" * 70)
    print("📊 UPDATE COMPLETE")
    print("=" * 70)
    print(f"Jobs processed: {total}")
    print(f"Jobs updated with skills: {updated}")
    print(f"Jobs still without skills: {still_empty}")
    
    success_rate = (updated / total * 100) if total > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    print("=" * 70)

if __name__ == "__main__":
    update_missing_skills()