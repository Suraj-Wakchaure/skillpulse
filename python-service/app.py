from src.analytics.skill_gap_analyzer import analyze_skill_gap
from bson import ObjectId # 🔥 Make sure this is imported at the top of app.py!
from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import sys
import os
import threading
import bcrypt
import jwt
import datetime
from functools import wraps
from src.database import jobs_collection, trends_collection, user_paths_collection, users_collection

# 🔥 ADD THESE TWO IMPORTS
from groq import Groq
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from collections import Counter

# 🔥 INITIALIZE GROQ CLIENT
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# 🔥 PRODUCTION CORS SECURITY
allowed_origins = [
    'http://localhost:3000',              # Local React development
    'https://skillpulse.vercel.app',      # Final Production Vercel frontend
    r'^https://skillpulse-.*\.vercel\.app$' # Vercel preview branches
]
CORS(app, origins=allowed_origins, supports_credentials=True)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get current database statistics"""
    try:
        total_jobs = jobs_collection.count_documents({})
        jobs_with_skills = jobs_collection.count_documents({'skills': {'$exists': True, '$ne': []}})
        
        # Get unique skills
        jobs = list(jobs_collection.find({'skills': {'$exists': True, '$ne': []}}))
        all_skills = set()
        total_mentions = 0
        
        for job in jobs:
            skills = job.get('skills', [])
            all_skills.update(skills)
            total_mentions += len(skills)
        
        avg_skills = total_mentions / jobs_with_skills if jobs_with_skills > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'totalJobs': total_jobs,
                'jobsWithSkills': jobs_with_skills,
                'uniqueSkills': len(all_skills),
                'avgSkillsPerJob': round(avg_skills, 1),
                'sources': ['Adzuna', 'Remotive', 'JSearch']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/skills/top', methods=['GET'])
def get_top_skills():
    """Get top 10 in-demand skills"""
    try:
        jobs = list(jobs_collection.find({'skills': {'$exists': True, '$ne': []}}))
        
        skill_counts = Counter()
        for job in jobs:
            skill_counts.update(job.get('skills', []))
        
        top_skills = []
        for rank, (skill, count) in enumerate(skill_counts.most_common(10), 1):
            percentage = (count / len(jobs) * 100) if jobs else 0
            top_skills.append({
                'rank': rank,
                'skill': skill,
                'jobs': count,
                'percentage': f"{percentage:.1f}%"
            })
        
        return jsonify({'success': True, 'data': top_skills})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Get latest trending skills"""
    try:
        all_trends = list(trends_collection.find())
        
        if not all_trends:
            return jsonify({
                'success': True,
                'data': {'rising': [], 'declining': []}
            })
        
        # Get latest week
        latest_week = max(t['week'] for t in all_trends)
        latest = [t for t in all_trends if t.get('week') == latest_week]
        
        rising = []
        declining = []
        
        for t in latest:
            pct = t.get('percentChange', 0)
            mentions = t.get('mentionCount', 0)
            
            # 🔥 Skip skills with tiny sample sizes (noise)
            if mentions < 3:
                continue
                
            # 🔥 Pure Math Logic: If > 0 it's rising, if < 0 it's declining
            if pct > 0:
                change_str = 'NEW' if pct >= 100 else f"+{pct:.1f}%"
                rising.append({
                    'skill': t['skill'],
                    'change': change_str,
                    'jobs': mentions,
                    'pct_val': pct
                })
            elif pct < 0:
                change_str = f"{pct:.1f}%"
                declining.append({
                    'skill': t['skill'],
                    'change': change_str,
                    'jobs': mentions,
                    'pct_val': pct
                })
                
        # Sort so the highest risers and biggest drops are at the top
        rising = sorted(rising, key=lambda x: x['pct_val'], reverse=True)[:10]
        declining = sorted(declining, key=lambda x: x['pct_val'])[:10] # Sorts most negative first
        
        return jsonify({
            'success': True,
            'data': {'rising': rising, 'declining': declining}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get skill category breakdown"""
    try:
        from analytics.skill_normalizer import get_skill_category
        
        jobs = list(jobs_collection.find({'skills': {'$exists': True, '$ne': []}}))
        
        all_skills = []
        for job in jobs:
            all_skills.extend(job.get('skills', []))
        
        category_counts = Counter()
        for skill in all_skills:
            category = get_skill_category(skill)
            category_counts[category] += 1
        
        total_mentions = len(all_skills)
        
        categories = []
        for category, count in category_counts.most_common():
            percentage = (count / total_mentions * 100) if total_mentions > 0 else 0
            categories.append({
                'category': category,
                'mentions': count,
                'percentage': f"{percentage:.1f}%"
            })
        
        return jsonify({'success': True, 'data': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/collect', methods=['POST'])
def collect_jobs():
    """Trigger job collection in the background"""
    try:
        def run_script():
            print("Background job collection started...")
            subprocess.run(
                [sys.executable, 'src/collect_all_jobs.py'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            print("Background job collection finished.")

        # Start the script in a separate thread
        thread = threading.Thread(target=run_script)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Job collection started in the background! Check the server console for progress.'
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting collection: {str(e)}'
        }), 500

@app.route('/api/skill-gap', methods=['POST'])
def analyze_skill_gap():
    try:
        data = request.json
        user_skills = [s.lower().strip() for s in data.get('skills', [])]
        target_role = data.get('role', '')

        if not target_role:
            return jsonify({'success': False, 'error': 'Target role is required'}), 400

        # 1. THE REGEX FIX + ONLY FETCHING JOBS WITH SKILLS
        matching_jobs = list(jobs_collection.find({
            'title': {'$regex': target_role, '$options': 'i'},
            'skills': {'$exists': True, '$ne': [], '$not': {'$size': 0}}
        }))

        total_jobs = len(matching_jobs)

        if total_jobs == 0:
            return jsonify({
                'success': True, 
                'data': {'error': f"No matching jobs with full skill data found for '{target_role}'. Try a broader role like 'Software Developer' or 'Data Engineer'."}
            })

        # 2. Extract and count all skills from these valid jobs
        skill_counts = {}
        for job in matching_jobs:
            for skill in job.get('skills', []):
                clean_skill = skill.lower().strip()
                skill_counts[clean_skill] = skill_counts.get(clean_skill, 0) + 1

        # Extract Top Companies
        company_counts = {}
        for job in matching_jobs:
            company_name = job.get('company', 'Unknown')
            if company_name and company_name.lower() not in ['unknown', 'confidential']:
                company_counts[company_name] = company_counts.get(company_name, 0) + 1
        
        # Get the top 5 companies by job count
        top_companies = [comp for comp, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

        # 3. Calculate percentages and find missing skills
        missing_skills = []
        user_has_count = 0
        
        for skill, count in skill_counts.items():
            percentage = round((count / total_jobs) * 100, 1)
            
            if skill in user_skills:
                user_has_count += 1
            else:
                # Only care about skills that appear in at least 10% of jobs
                if percentage > 10:
                    priority = "CRITICAL" if percentage >= 40 else "HIGH" if percentage >= 20 else "MEDIUM"
                    est_time = "6-8 weeks" if percentage >= 40 else "4-6 weeks" if percentage >= 20 else "2-4 weeks"
                    
                    missing_skills.append({
                        'skill': skill,
                        'count': count,
                        'percentage': percentage,
                        'priority': priority,
                        'estimated_time': est_time
                    })

        # Sort missing skills by highest percentage
        missing_skills = sorted(missing_skills, key=lambda x: x['percentage'], reverse=True)[:10]

        # Add ranking order
        for idx, item in enumerate(missing_skills, 1):
            item['learn_order'] = idx

        # Calculate Match Score
        total_unique_market_skills = len(skill_counts.keys())
        match_score = round((user_has_count / min(15, total_unique_market_skills)) * 100) if total_unique_market_skills > 0 else 0
        match_score = min(100, match_score) # Cap at 100%

        # 4. GENERATE AI ROADMAP (WITH INCREASED MAX_TOKENS)
        top_5_missing = [s['skill'] for s in missing_skills[:5]]
        
        prompt = f"""
        Act as an expert career mentor. The user wants to become a {target_role}.
        They already know: {', '.join(user_skills) if user_skills else 'Nothing yet'}.
        
        Based on our database, they are missing these top 5 priority skills: {', '.join(top_5_missing)}.
        
        Write a concise, highly specific learning roadmap. For each of the 5 missing skills, provide:
        - Why it is critical for a {target_role}
        - When they should learn it (e.g., Immediately, After learning X)
        
        Keep formatting clean and easy to read. Do not cut off mid-sentence.
        """
        
        ai_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1500  # 🔥 INCREASED LIMIT SO IT DOESN'T CUT OFF
        )
        
        roadmap_text = ai_response.choices[0].message.content
        
        # # --- ✅ ADD THIS FAKE TEXT INSTEAD ✅ ---
        # roadmap_text = f"AI Roadmap is temporarily paused to save tokens! \n\nBut the math is working perfectly. Your top skills to focus on are: {', '.join(top_5_missing)}"

        return jsonify({
            'success': True,
            'data': {
                'total_jobs': total_jobs,
                'match_percentage': match_score,
                'skills_you_have': [s for s in user_skills if s in skill_counts],
                'skills_missing': missing_skills,
                'top_companies': top_companies,
                'ai_roadmap': roadmap_text
            }
        })

    except Exception as e:
        print(f"Error in skill gap analysis: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trends-chart', methods=['GET'])
def get_trends_chart():
    from src.database import trends_collection
    
    # Get latest week
    latest = trends_collection.find().sort("week", -1).limit(1)
    latest_week = None
    
    for item in latest:
        latest_week = item['week']
    
    if not latest_week:
        return {"success": False, "message": "No data"}
    
    # Get top skills for that week
    trends = list(trends_collection.find({"week": latest_week}))
    
    # Sort by demand (current_count)
    trends.sort(key=lambda x: x.get('mentionCount', 0), reverse=True)

    top = trends[:10]

    labels = [t['skill'] for t in top]
    values = [t.get('mentionCount', 0) for t in top]
    
    return {
        "success": True,
        "data": {
            "labels": labels,
            "values": values
        }
    }



@app.route('/api/paths/save', methods=['POST'])
def save_learning_path():
    try:
        data = request.json
        user_email = data.get('email') # Using email to identify the user
        role = data.get('role')
        missing_skills = data.get('missing_skills', [])
        
        if not user_email or not role:
            return jsonify({'success': False, 'error': 'Missing user or role data'}), 400

        # Check the limit!
        existing_paths = list(user_paths_collection.find({'user_email': user_email}))
        if len(existing_paths) >= 3:
            return jsonify({'success': False, 'limit_reached': True, 'message': 'You can only have 3 active learning paths. Please delete one to add a new one.'})

        # Create dynamic steps based on the missing skills
        steps = []
        for index, skill in enumerate(missing_skills[:5]): # Take top 5 missing skills
            steps.append({
                'id': index + 1,
                'title': f"Master {skill['skill'].capitalize()}",
                'description': f"Priority: {skill['priority']}. Estimated time: {skill['estimated_time']}.",
                'skills': [skill['skill'].capitalize()],
                'status': 'active' if index == 0 else 'locked', # First one is active, rest locked
                'duration': skill['estimated_time']
            })

        new_path = {
            'user_email': user_email,
            'target_role': role,
            'progress': 0,
            'steps': steps,
            'created_at': "2026-04-12" # Can use datetime.now() here
        }

        user_paths_collection.insert_one(new_path)
        return jsonify({'success': True, 'message': 'Successfully saved to Learning Path!'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paths/<user_email>', methods=['GET'])
def get_learning_paths(user_email):
    try:
        paths = list(user_paths_collection.find({'user_email': user_email}))
        # Convert ObjectId to string for JSON serialization
        for path in paths:
            path['_id'] = str(path['_id'])
            
        return jsonify({'success': True, 'data': paths})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paths/<path_id>', methods=['DELETE'])
def delete_learning_path(path_id):
    try:
        # Delete the specific path using its unique MongoDB ID
        result = user_paths_collection.delete_one({'_id': ObjectId(path_id)})
        
        if result.deleted_count == 1:
            return jsonify({'success': True, 'message': 'Path successfully deleted'})
        else:
            return jsonify({'success': False, 'error': 'Path not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/paths/<path_id>/progress', methods=['PUT'])
def update_path_progress(path_id):
    try:
        data = request.json
        completed_steps = data.get('completed_steps', [])
        progress = data.get('progress', 0)

        # Update the specific path in MongoDB
        result = user_paths_collection.update_one(
            {'_id': ObjectId(path_id)},
            {'$set': {
                'completed_steps': completed_steps, 
                'progress': progress
            }}
        )
        
        if result.matched_count == 1:
            return jsonify({'success': True, 'message': 'Progress saved'})
        else:
            return jsonify({'success': False, 'error': 'Path not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'Student')

    if not email or not password or not name:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    # 1. Check if user already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'success': False, 'error': 'Email already registered'}), 409

    # 2. Hash the password using Bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # 3. Save to database
    new_user = {
        'name': name,
        'email': email,
        'password': hashed_password, # Never save plain text!
        'role': role,
        'created_at': datetime.datetime.utcnow()
    }
    
    users_collection.insert_one(new_user)
    return jsonify({'success': True, 'message': 'User created successfully'})


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Missing email or password'}), 400

    # 1. Find user in DB
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    # 2. Check password matches the hash
    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        # 3. Generate JWT Token (valid for 7 days)
        token = jwt.encode({
            'email': user['email'],
            'name': user['name'],
            'role': user.get('role', 'Student'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'success': True,
            'token': token,
            'user': {'name': user['name'], 'email': user['email'], 'role': user.get('role', 'Student')}
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    print("=" * 70)
    print("SkillPulse Flask API Server")
    print("=" * 70)
    print("Server running on: http://localhost:5001")
    print("API Endpoints:")
    print("  GET  /api/stats      - Database statistics")
    print("  GET  /api/skills/top - Top 10 skills")
    print("  GET  /api/trends     - Trending skills")
    print("  GET  /api/categories - Skill categories")
    print("  POST /api/collect    - Trigger job collection")
    print("=" * 70)
    
    # 🔥 PRODUCTION PORT BINDING (Required for Render)
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)