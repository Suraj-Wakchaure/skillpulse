import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import jobs_collection
from analytics.skill_normalizer import normalize_skill_list

def normalize_all_jobs():
    """Normalize skills in all job documents"""
    
    SEP = "=" * 70
    
    print(SEP)
    print("NORMALIZING SKILLS IN ALL JOBS")
    print(SEP)
    
    jobs = list(jobs_collection.find({'skills': {'$exists': True, '$ne': []}}))
    total = len(jobs)
    
    print(f"\nFound {total} jobs with skills")
    print("Starting normalization...\n")
    
    updated = 0
    unchanged = 0
    examples = []
    
    for idx, job in enumerate(jobs, 1):
        original_skills = job.get('skills', [])
        normalized_skills = normalize_skill_list(original_skills)
        
        # Check if anything changed
        if set(original_skills) != set(normalized_skills):
            # Update in database
            jobs_collection.update_one(
                {'_id': job['_id']},
                {'$set': {'skills': normalized_skills}}
            )
            updated += 1
            
            # Save first 3 examples
            if len(examples) < 3:
                examples.append({
                    'title': job.get('title', 'N/A')[:40],
                    'before': original_skills[:5],
                    'after': normalized_skills[:5]
                })
        else:
            unchanged += 1
        
        if idx % 25 == 0:
            print(f"Progress: {idx}/{total} | Updated: {updated} | Unchanged: {unchanged}")
    
    print(f"\nFinal: {total}/{total} | Updated: {updated} | Unchanged: {unchanged}")
    
    # Show examples
    if examples:
        print(f"\n📝 Example Changes:")
        print("-" * 70)
        for i, ex in enumerate(examples, 1):
            print(f"\n{i}. {ex['title']}")
            print(f"   Before: {ex['before']}")
            print(f"   After:  {ex['after']}")
    
    print("\n" + SEP)
    print("📊 NORMALIZATION COMPLETE")
    print(SEP)
    print(f"Total jobs: {total}")
    print(f"Jobs updated: {updated} ({updated/total*100:.1f}%)")
    print(f"Jobs unchanged: {unchanged} ({unchanged/total*100:.1f}%)")
    print(SEP)

if __name__ == "__main__":
    normalize_all_jobs()