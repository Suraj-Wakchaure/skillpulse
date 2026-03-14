import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import jobs_collection
from collections import Counter

def check_for_duplicates():
    """Find potential duplicate skills in database"""
    
    print("=" * 70)
    print("CHECKING FOR DUPLICATE SKILLS")
    print("=" * 70)
    
    # Get all skills
    all_skills = []
    jobs = list(jobs_collection.find())
    
    for job in jobs:
        skills = job.get('skills', [])
        all_skills.extend(skills)
    
    # Count occurrences
    skill_counts = Counter(all_skills)
    
    # Group similar skills
    potential_duplicates = {}
    
    for skill in skill_counts.keys():
        base = skill.lower().replace('.js', '').replace('js', '').replace(' ', '').replace('-', '')
        
        if base not in potential_duplicates:
            potential_duplicates[base] = []
        potential_duplicates[base].append({
            'name': skill,
            'count': skill_counts[skill]
        })
    
    # Find groups with multiple variations
    print("\n🔍 Potential Duplicate Skill Groups:")
    print("=" * 70)
    
    duplicates_found = 0
    
    for base, variations in potential_duplicates.items():
        if len(variations) > 1:
            duplicates_found += 1
            total_count = sum(v['count'] for v in variations)
            
            print(f"\n{duplicates_found}. Base: '{base}' → Total mentions: {total_count}")
            for var in sorted(variations, key=lambda x: x['count'], reverse=True):
                print(f"   - '{var['name']}': {var['count']} jobs")
    
    if duplicates_found == 0:
        print("\n✅ No obvious duplicates found!")
    else:
        print("\n" + "=" * 70)
        print(f"Found {duplicates_found} potential duplicate groups")
        print("These should be normalized to single canonical names")
        print("=" * 70)

if __name__ == "__main__":
    check_for_duplicates()