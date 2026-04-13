import sys
import os
sys.path.append(os.path.dirname(__file__))
from database import trends_collection

def view_latest_trends():
    """View latest trending skills"""
    
    print("=" * 70)
    print("LATEST SKILL TRENDS")
    print("=" * 70)
    
    # Get all trends
    trends = list(trends_collection.find())
    
    if not trends:
        print("\nNo trend data found!")
        print("Run: python src/analytics/trend_calculator.py")
        return
    
    # Get latest week
    latest_week = max(t['week'] for t in trends)
    
    print(f"\nLatest Week: {latest_week}")
    
    # Filter for latest week
    latest = [t for t in trends if t.get('week') == latest_week]
    
    # Group by direction
    rising = [t for t in latest if t.get('trendDirection') == 'rising']
    declining = [t for t in latest if t.get('trendDirection') == 'declining']
    stable = [t for t in latest if t.get('trendDirection') == 'stable']
    
    print(f"\nTrend Summary:")
    print(f"  Rising: {len(rising)} skills")
    print(f"  Declining: {len(declining)} skills")
    print(f"  Stable: {len(stable)} skills")
    
    # Show top rising
    if rising:
        print(f"\nTOP RISING SKILLS:")
        print("-" * 70)
        print(f"{'Rank':<6} {'Skill':<30} {'Change':<10} {'Current Jobs'}")
        print("-" * 70)
        
        sorted_rising = sorted(rising, key=lambda x: x.get('percentChange', 0), reverse=True)[:15]
        
        for i, trend in enumerate(sorted_rising, 1):
            skill = trend['skill']
            change = trend.get('percentChange', 0)
            count = trend.get('mentionCount', 0)
            
            # Display "NEW" for 100% instead of percentage
            if change >= 100:
                change_str = "NEW"
            else:
                change_str = f"+{change:.1f}%"
            
            print(f"{i:<6} {skill:<30} {change_str:<10} {count}")
    
    # Show top declining
    if declining:
        print(f"\nTOP DECLINING SKILLS:")
        print("-" * 70)
        print(f"{'Rank':<6} {'Skill':<30} {'Change':<10} {'Current Jobs'}")
        print("-" * 70)
        
        sorted_declining = sorted(declining, key=lambda x: x.get('percentChange', 0))[:15]
        
        for i, trend in enumerate(sorted_declining, 1):
            skill = trend['skill']
            change = trend.get('percentChange', 0)
            count = trend.get('mentionCount', 0)
            print(f"{i:<6} {skill:<30} {change:.1f}%{'':<4} {count}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    view_latest_trends()