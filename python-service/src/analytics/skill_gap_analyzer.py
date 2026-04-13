import os
import re
from collections import Counter
from pathlib import Path
import sys

# Robust path resolution
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.database import jobs_collection, trends_collection
from groq import Groq
from dotenv import load_dotenv
from src.analytics.skill_normalizer import get_skill_category

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_skill_gap(user_skills, role=None):
    # 1. Normalize user skills
    user_skills = [s.strip().lower() for s in user_skills]

    # 2. Query jobs efficiently (Title ONLY to prevent DB timeouts)
    query = {'skills': {'$exists': True, '$ne': []}}
    
    if role:
        # Try exact match first
        query['title'] = {'$regex': re.escape(role), '$options': 'i'}
        jobs = list(jobs_collection.find(query).limit(200))
        
        # Fallback: Search for ALL partial words (AND logic)
        if not jobs:
            del query['title']  # Remove the failed exact match
            words = [re.escape(w) for w in role.lower().split() if len(w) > 1] # Catch 2-letter words like "AI", "ML"
            if words:
                query['$and'] = [{'title': {'$regex': w, '$options': 'i'}} for w in words]
                jobs = list(jobs_collection.find(query).limit(200))
    else:
        jobs = list(jobs_collection.find(query).limit(200))

    if not jobs:
        return {"error": f"No matching jobs found in database for role: '{role}'. Try a different role."}

    total_jobs = len(jobs)
    total_db_jobs = max(jobs_collection.count_documents({}), 1)

    # 3. Collect and count skills
    all_skills = []
    for job in jobs:
        all_skills.extend([s.lower() for s in job.get('skills', [])])
    
    skill_counts = Counter(all_skills)

    # 4. Dominant Category Calculation
    category_counts = {}
    for s, c in skill_counts.items():
        cat = get_skill_category(s)
        category_counts[cat] = category_counts.get(cat, 0) + c
    
    dominant_category = max(category_counts, key=category_counts.get) if category_counts else "Other"

    # 5. Top Role Skills (for co-occurrence)
    top_role_skills = [s for s, c in skill_counts.most_common(10) if c / total_jobs < 0.6][:5]

    # 6. Co-occurrence Map
    co_occurrence = {}
    for job in jobs:
        skills = [s.lower() for s in job.get('skills', [])]
        for s1 in skills:
            for s2 in skills:
                if s1 == s2: continue
                if s1 not in co_occurrence: co_occurrence[s1] = Counter()
                co_occurrence[s1][s2] += 1

    # 7. Fetch Trends ONCE (This prevents the infinite loading!)
    all_trends = list(trends_collection.find())
    trend_dict = {t['skill'].lower(): t.get('ml_slope', 0) for t in all_trends}

    # 8. Build Skill Data
    skill_data = []
    for skill, count in skill_counts.items():
        percentage = (count / total_jobs) * 100
        if percentage < 3: continue

        category = get_skill_category(skill)
        
        # Instant penalty calculation (No DB query needed)
        penalty = (count / total_db_jobs) * 20

        if role:
            role_lower = role.lower()
            if "data" in role_lower and category not in ["AI/ML", "Database"]: penalty += 10
            if "devops" in role_lower and category not in ["DevOps", "Cloud"]: penalty += 10
            if "web" in role_lower and category not in ["Frontend", "Backend"]: penalty += 10
            if "ai" in role_lower and category not in ["AI/ML"]: penalty += 10
        
        category_score = 5 if category == dominant_category else 0
        
        related = co_occurrence.get(skill, {})
        relevance = sum(related.get(core, 0) for core in top_role_skills)
        
        if role and relevance == 0 and percentage < 10:
            continue

        slope = trend_dict.get(skill.lower(), 0)
        top_related = [k for k, v in related.most_common(3)]

        skill_data.append({
            'skill': skill,
            'percentage': round(percentage, 1),
            'ml_slope': slope,
            'related_skills': top_related,
            'penalty': penalty,
            'category_score': category_score
        })

    skill_data.sort(key=lambda x: x['percentage'], reverse=True)

    # 9. Prioritize Missing Skills
    user_has = []
    missing = []
    for skill in skill_data:
        if skill['skill'] in user_skills:
            user_has.append(skill)
        else:
            pct = skill['percentage']
            related = co_occurrence.get(skill['skill'], {})
            relevance = sum(related.get(core, 0) for core in top_role_skills)
            co_score = relevance * 1.5

            score = pct + (skill['ml_slope'] * 5) + co_score + skill['category_score'] - skill['penalty']

            if score >= 35: priority = "CRITICAL"
            elif score >= 25: priority = "HIGH"
            elif score >= 15: priority = "MEDIUM"
            else: priority = "LOW"

            skill['priority'] = priority
            missing.append(skill)

    priority_order = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "LOW": 0}
    missing.sort(key=lambda x: (priority_order[x['priority']], x['ml_slope'], x['percentage']), reverse=True)

    for idx, skill in enumerate(missing, 1):
        skill['learn_order'] = idx
        if skill['priority'] == "CRITICAL": skill['estimated_time'] = "6-8 weeks"
        elif skill['priority'] == "HIGH": skill['estimated_time'] = "4-6 weeks"
        elif skill['priority'] == "MEDIUM": skill['estimated_time'] = "2-4 weeks"
        else: skill['estimated_time'] = "1-2 weeks"

    top_skills = skill_data[:20]
    user_has_count = sum(1 for s in top_skills if s['skill'] in user_skills)
    match_percentage = (user_has_count / len(top_skills)) * 100 if top_skills else 0

    roadmap = generate_ai_roadmap(missing, role)

    return {
        "total_jobs": total_jobs,
        "match_percentage": round(match_percentage, 1),
        "skills_you_have": user_has[:10],
        "skills_missing": missing[:10],
        "ai_roadmap": roadmap
    }

def generate_ai_roadmap(skills_missing, role):
    if not skills_missing:
        return "You have all the required skills for this role!"
        
    top_skills = skills_missing[:min(6, len(skills_missing))]
    skill_text = "\n".join([
        f"{i+1}. {s['skill']} (Priority: {s['priority']})" for i, s in enumerate(top_skills)
    ])

    prompt = f"""You are a career mentor.
Target Role: {role if role else 'Software Developer'}
These are missing skills ranked by importance:
{skill_text}
Format:
1. Skill Name
   - Why
   - When
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "AI roadmap generation failed."