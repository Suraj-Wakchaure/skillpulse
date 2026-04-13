import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import jobs_collection

print("=" * 70)
print("ANALYZING FAILED SKILL EXTRACTIONS")
print("=" * 70)

# Get jobs with no skills
failed_jobs = list(jobs_collection.find({'skills': []}).limit(10))

print(f"\nFound {jobs_collection.count_documents({'skills': []})} jobs with no skills")

print("\nSample Failed Jobs:")
print("=" * 70)

for i, job in enumerate(failed_jobs, 1):
    desc = job.get('description', 'N/A')
    desc_length = len(desc) if desc and desc != 'N/A' else 0
    
    print(f"\n{i}. {job['title']}")
    print(f"   Company: {job['company']}")
    print(f"   Source: {job['source']}")
    print(f"   Description length: {desc_length} chars")
    
    if desc_length < 100:
        print(f"   Description too short!")
    
    if desc_length > 0:
        print(f"   Preview: {desc[:150]}...")

print("\n" + "=" * 70)