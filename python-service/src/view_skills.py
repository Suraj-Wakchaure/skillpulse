import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import jobs_collection
from collections import Counter

def view_skill_stats():
    """View skill statistics from collected jobs"""
    print("=" * 70)
    print("SKILL DEMAND ANALYSIS")
    print("=" * 70)
    
    # Get all jobs
    jobs = list(jobs_collection.find())
    total_jobs = len(jobs)
    
    if total_jobs == 0:
        print("No jobs in database yet!")
        return
    
    print(f"\nAnalyzing {total_jobs} jobs...")
    
    # Count all skills
    all_skills = []
    jobs_with_skills = 0
    
    for job in jobs:
        skills = job.get('skills', [])
        if skills:
            jobs_with_skills += 1
            # Convert to set to ensure no duplicates from same job
            all_skills.extend(set(skills))  # ← ADDED set() here
    
    if not all_skills:
        print("No skills extracted yet!")
        print(f"Jobs without skills: {total_jobs - jobs_with_skills}")
        return
    
    # Count frequency
    skill_counts = Counter(all_skills)
    
    # Calculate percentages
    print(f"\nTOP 20 IN-DEMAND SKILLS:")
    print("=" * 70)
    print(f"{'Rank':<6} {'Skill':<30} {'Jobs':<10} {'% of Jobs*':<12}")  # ← Changed header
    print("-" * 70)
    
    for rank, (skill, count) in enumerate(skill_counts.most_common(20), 1):
        # FIXED: Calculate based on jobs_with_skills, not total_jobs
        percentage = (count / jobs_with_skills) * 100  # ← CRITICAL FIX
        print(f"{rank:<6} {skill:<30} {count:<10} {percentage:.1f}%")
    
    print("\n" + "=" * 70)
    print(f"Total jobs in database: {total_jobs}")
    print(f"Jobs with skills extracted: {jobs_with_skills} ({jobs_with_skills/total_jobs*100:.1f}%)")  # ← ADDED
    print(f"Jobs without skills: {total_jobs - jobs_with_skills}")
    print(f"Total unique skills found: {len(skill_counts)}")
    print(f"Total skill mentions: {len(all_skills)}")
    if jobs_with_skills > 0:
        print(f"Average skills per job: {len(all_skills) / jobs_with_skills:.1f}")
    print("\n* Percentage = (jobs with this skill / jobs with any skills)")  # ← ADDED note
    print("=" * 70)

if __name__ == "__main__":
    view_skill_stats()