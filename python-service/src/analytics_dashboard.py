"""
Complete Analytics Dashboard
Shows all insights: top skills, trends, coverage stats
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import jobs_collection, trends_collection
from collections import Counter

def show_analytics_dashboard():
    """Display complete analytics overview"""
    
    SEP = "=" * 70
    
    print(SEP)
    print("SKILLPULSE ANALYTICS DASHBOARD")
    print(SEP)
    
    # 1. Database Stats
    total_jobs = jobs_collection.count_documents({})
    jobs_with_skills = jobs_collection.count_documents({'skills': {'$exists': True, '$ne': []}})
    
    print(f"\nDATABASE STATISTICS:")
    print("-" * 70)
    print(f"Total Jobs: {total_jobs}")
    print(f"Jobs with Skills: {jobs_with_skills} ({jobs_with_skills/total_jobs*100:.1f}%)")
    print(f"Jobs without Skills: {total_jobs - jobs_with_skills}")
    
    # 2. Skill Coverage
    jobs = list(jobs_collection.find({'skills': {'$exists': True, '$ne': []}}))
    all_skills = []
    for job in jobs:
        all_skills.extend(job.get('skills', []))
    
    skill_counts = Counter(all_skills)
    
    print(f"\nSKILL COVERAGE:")
    print("-" * 70)
    print(f"Unique Skills Tracked: {len(skill_counts)}")
    print(f"Total Skill Mentions: {len(all_skills)}")
    print(f"Average Skills per Job: {len(all_skills)/jobs_with_skills:.1f}")
    
    # 3. Top 10 Skills
    print(f"\nTOP 10 IN-DEMAND SKILLS:")
    print("-" * 70)
    print(f"{'Rank':<6} {'Skill':<30} {'Jobs':<8} {'% of Jobs'}")
    print("-" * 70)
    
    for rank, (skill, count) in enumerate(skill_counts.most_common(10), 1):
        percentage = (count / jobs_with_skills) * 100
        print(f"{rank:<6} {skill:<30} {count:<8} {percentage:.1f}%")
    
    # 3.5 Skill Categories (NEW)
    from analytics.skill_normalizer import get_skill_category

    print(f"\nSKILL CATEGORY BREAKDOWN:")
    print("-" * 70)

    categories = {}
    for skill in all_skills:
        category = get_skill_category(skill)
        categories[category] = categories.get(category, 0) + 1

    total_skill_mentions = len(all_skills)

    print(f"{'Category':<20} {'Mentions':<12} {'% of Total'}")
    print("-" * 70)

    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_skill_mentions) * 100
        print(f"{category:<20} {count:<12} {percentage:.1f}%")
    
    # 4. Trend Summary
    trends = list(trends_collection.find())
    
    if trends:
        latest_week = max(t['week'] for t in trends)
        latest_trends = [t for t in trends if t.get('week') == latest_week]
        
        rising = [t for t in latest_trends if t.get('trendDirection') == 'rising']
        declining = [t for t in latest_trends if t.get('trendDirection') == 'declining']
        
        print(f"\nTREND SUMMARY (Week {latest_week}):")
        print("-" * 70)
        print(f"Rising Skills: {len(rising)}")
        print(f"Declining Skills: {len(declining)}")
        print(f"Stable Skills: {len(latest_trends) - len(rising) - len(declining)}")
        
        if rising:
            top_rising = sorted(rising, key=lambda x: x.get('percentChange', 0), reverse=True)[0]
            print(f"\nHottest Skill: {top_rising['skill']} (+{top_rising.get('percentChange', 0):.1f}%)")
    else:
        print(f"\nTRENDS:")
        print("-" * 70)
        print("No trend data available. Run trend calculator.")
    
    # 5. Data Sources
    sources = {}
    for job in jobs_collection.find():
        source = job.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\nDATA SOURCES:")
    print("-" * 70)
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"{source}: {count} jobs ({count/total_jobs*100:.1f}%)")
    
    # 6. Time Coverage
    jobs_with_dates = list(jobs_collection.find({'posted_date': {'$exists': True, '$ne': None}}))
    
    if jobs_with_dates:
        from datetime import datetime
        dates = []
        for job in jobs_with_dates:
            pd = job.get('posted_date')
            if isinstance(pd, str):
                try:
                    dates.append(datetime.fromisoformat(pd.replace('Z', '+00:00')))
                except:
                    pass
            elif isinstance(pd, datetime):
                dates.append(pd)
        
        if dates:
            oldest = min(dates)
            newest = max(dates)
            days_span = (newest - oldest).days
            
            print(f"\nTIME COVERAGE:")
            print("-" * 70)
            print(f"Oldest Job: {oldest.strftime('%Y-%m-%d')}")
            print(f"Newest Job: {newest.strftime('%Y-%m-%d')}")
            print(f"Data Span: {days_span} days ({days_span//7} weeks)")
    
    print("\n" + SEP)
    print("Dashboard generated successfully!")
    print(SEP)

if __name__ == "__main__":
    show_analytics_dashboard()