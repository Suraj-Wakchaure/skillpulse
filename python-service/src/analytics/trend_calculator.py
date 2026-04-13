"""
Trend Calculation Module
Calculates weekly skill trends and identifies trending UP/DOWN skills
"""

from datetime import datetime, timedelta
from collections import defaultdict
import sys
import os
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
from database import jobs_collection, trends_collection

def predict_trend_linear(weekly_counts):
    """
    Simple Linear Regression:
    x = week index
    y = skill count
    
    Returns slope (trend direction)
    """
    
    n = len(weekly_counts)
    
    if n < 2:
        return 0
    
    x = list(range(n))          # [0,1,2,3...]
    y = weekly_counts          # skill counts
    
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0
    
    slope = numerator / denominator
    
    return round(slope, 2)

def calculate_weekly_trends():
    """
    Calculate skill trends by grouping jobs into weekly buckets
    based on posted_date
    """
    
    print("=" * 70)
    print("CALCULATING WEEKLY SKILL TRENDS")
    print("=" * 70)
    
    # Get all jobs with skills
    jobs = list(jobs_collection.find({
        'skills': {'$exists': True, '$ne': []},
        'posted_date': {'$exists': True, '$ne': None}
    }))
    
    if len(jobs) == 0:
        print("\nNo jobs with posted_date found!")
        print("Cannot calculate trends without time-series data.")
        return
    
    print(f"\nFound {len(jobs)} jobs with posted dates")
    
    # Group jobs by week
    weekly_data = defaultdict(lambda: defaultdict(int))
    
    for job in jobs:
        posted_date = job.get('posted_date')
        
        # Convert to datetime if string
        if isinstance(posted_date, str):
            try:
                posted_date = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
            except:
                continue
        
        if not isinstance(posted_date, datetime):
            continue
        
        # Get week start (Monday)
        week_start = posted_date - timedelta(days=posted_date.weekday())
        week_key = week_start.strftime('%Y-%m-%d')
        
        # Count skills for this week
        for skill in job.get('skills', []):
            weekly_data[week_key][skill] += 1
    
    # Sort weeks
    sorted_weeks = sorted(weekly_data.keys())
    
    print(f"\nData spans {len(sorted_weeks)} weeks:")
    for week in sorted_weeks:
        total_skills = sum(weekly_data[week].values())
        print(f"  Week {week}: {len(weekly_data[week])} unique skills, {total_skills} total mentions")
    
    # Calculate trends (week-over-week changes)
    if len(sorted_weeks) < 2:
        print("\nNeed at least 2 weeks of data to calculate trends")
        print("Saving weekly aggregates for future trend calculation...")
        save_weekly_aggregates(weekly_data, sorted_weeks)
        return
    
    print(f"\nCalculating trends...")
    
    trends = []
    
    # Compare each week with previous week
    for i in range(1, len(sorted_weeks)):
        current_week = sorted_weeks[i]
        previous_week = sorted_weeks[i-1]
        
        current_data = weekly_data[current_week]
        previous_data = weekly_data[previous_week]
        
        # Get all skills from both weeks
        all_skills = set(current_data.keys()) | set(previous_data.keys())
        
        for skill in all_skills:
            current_count = current_data.get(skill, 0)
            previous_count = previous_data.get(skill, 0)
            
            # Get weekly history for this skill
            history = []

            for week in sorted_weeks:
                history.append(weekly_data[week].get(skill, 0))

            # Predict trend using linear regression
            slope = predict_trend_linear(history)
            # FIXED: Only track skills with meaningful presence
            # Skip if total mentions across both weeks < 4
            if (current_count + previous_count) < 4:
                continue
            
            # Skip if both weeks have < 2 mentions
            if previous_count < 2 and current_count < 2:
                continue
            
            # Calculate percent change
            if previous_count >= 2:
                # Normal calculation for established skills
                percent_change = ((current_count - previous_count) / previous_count) * 100
            elif previous_count > 0:
                # Small base, calculate but cap display
                percent_change = min(((current_count - previous_count) / previous_count) * 100, 200)
            elif current_count >= 3:
                # New skill with good presence
                percent_change = 100
            else:
                continue
            
            # Determine trend direction
            if slope > 1:
                direction = 'rising'
            elif slope < -1:
                direction = 'declining'
            else:
                direction = 'stable'
            
            trends.append({
                'skill': skill,
                'week': current_week,
                'current_count': current_count,
                'previous_count': previous_count,
                'percent_change': round(percent_change, 1),
                'direction': direction,
                'ml_slope': slope,
            })
    
    # Save to database
    save_trends(trends)
    
    # Show trending skills
    show_trending_summary(trends, sorted_weeks[-1])
    
    print("\n" + "=" * 70)
    print("TREND CALCULATION COMPLETE")
    print("=" * 70)


def save_weekly_aggregates(weekly_data, weeks):
    """Save weekly skill counts"""
    print(f"\nSaving weekly aggregates to database...")
    
    saved = 0
    for week in weeks:
        for skill, count in weekly_data[week].items():
            trends_collection.update_one(
                {'skill': skill, 'week': week},
                {
                    '$set': {
                        'mentionCount': count,
                        'calculatedAt': datetime.now()
                    }
                },
                upsert=True
            )
            saved += 1
    
    print(f"Saved {saved} weekly skill records")


def save_trends(trends):
    """Save calculated trends to database"""
    if not trends:
        return
    
    print(f"\nSaving {len(trends)} trend records...")
    
    for trend in trends:
        trends_collection.update_one(
            {'skill': trend['skill'], 'week': trend['week']},
            {
                '$set': {
                    'mentionCount': trend['current_count'],
                    'percentChange': trend['percent_change'],
                    'trendDirection': trend['direction'],
                    'ml_slope': trend.get('ml_slope', 0),
                    'calculatedAt': datetime.now()
                }
            },
            upsert=True
        )
    
    print(f"Saved trends to database")


def show_trending_summary(trends, latest_week):
    """Show summary of trending skills"""
    
    # Filter for latest week only
    latest_trends = [t for t in trends if t['week'] == latest_week]
    
    if not latest_trends:
        return
    
    print(f"\nTRENDING SKILLS (Week {latest_week}):")
    print("=" * 70)
    
    # Top rising skills
    rising = sorted([t for t in latest_trends if t['direction'] == 'rising'], 
                   key=lambda x: x['percent_change'], reverse=True)[:10]
    
    if rising:
        print("\nTOP 10 RISING SKILLS:")
        print("-" * 70)
        for i, trend in enumerate(rising, 1):
            change_str = f"+{trend['percent_change']:.1f}%" if trend['percent_change'] < 100 else "NEW"
            print(f"{i:2}. {trend['skill']:30} {change_str:>8}  ({trend['previous_count']} → {trend['current_count']}) | ML slope: {trend.get('ml_slope', 0)}")
    
    # Top declining skills
    declining = sorted([t for t in latest_trends if t['direction'] == 'declining'], 
                      key=lambda x: x['percent_change'])[:10]
    
    if declining:
        print("\nTOP 10 DECLINING SKILLS:")
        print("-" * 70)
        for i, trend in enumerate(declining, 1):
            print(f"{i:2}. {trend['skill']:30} {trend['percent_change']:7.1f}%  ({trend['previous_count']} → {trend['current_count']}) | ML slope: {trend.get('ml_slope', 0)}")


# Test
if __name__ == "__main__":
    calculate_weekly_trends()