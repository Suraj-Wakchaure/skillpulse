from groq import Groq
import os
import json
import re
import time
from dotenv import load_dotenv
from html import unescape

load_dotenv()

# Initialize Groq client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

def clean_description(description):
    """Clean HTML and special characters from job description"""
    if not description:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', ' ', description)
    
    # Decode HTML entities (&nbsp; → space, etc.)
    clean_text = unescape(clean_text)
    
    # Remove extra whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    return clean_text.strip()


def extract_skills_from_description(job):
    """
    Extract technical skills using Groq Llama 3.1 70B
    """
    title = job.get('title', '').lower()
    description = job.get('description', '')
    
    TECH_HINTS = [
        'developer', 'engineer', 'software',
        'data', 'devops', 'cloud',
        'qa', 'test', 'analyst',
        'consultant', 'specialist', 'it'
    ]

    if not any(k in title for k in TECH_HINTS):
        return []
    
    if not description or len(description) < 30:
        return []
    
    # Clean the description
    description = clean_description(description)
    
    # Limit length
    description = description[:2500]
    
    # Skip if too short (less than 50 chars = likely no content)
    if len(description) < 50:
        return []
    
    # Enhanced prompt - more explicit
    prompt = f"""You are a technical skill extraction AI. Extract ALL technical skills from this job posting.

Technical skills include:
- Programming languages: Python, Java, JavaScript, PHP, C++, Go, Rust, etc.
- Frameworks: React, Angular, Vue, Django, Flask, Spring, Laravel, etc.
- Databases: MongoDB, MySQL, PostgreSQL, Redis, Cassandra, etc.
- Cloud: AWS, Azure, GCP, Docker, Kubernetes, etc.
- Mobile: Flutter, React Native, Swift, Kotlin, Android, iOS, etc.
- Tools: Git, Jenkins, Jira, Webpack, etc.
- Any other IT technology

Job Description:
{description}

Instructions:
1. Find ALL technical skills mentioned
2. Return as JSON array: ["skill1", "skill2", "skill3"]
3. Use standard names (React not React.js, Node.js not NodeJS)
4. If no skills found, return empty array: []
5. Do NOT include soft skills or job requirements like "experience"

JSON array of technical skills:"""

    try:
        # Call Groq API with optimized parameters
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You extract technical skills and return only valid JSON arrays. Be thorough."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,   # Very low for consistency
            max_tokens=500,    # More tokens for comprehensive extraction
            top_p=0.9
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean response - remove markdown, code blocks
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        
        # Try multiple JSON extraction patterns
        # Pattern 1: Standard array
        json_match = re.search(r'\[.*?\]', result_text, re.DOTALL)
        
        if json_match:
            skills_json = json_match.group(0)
            
            try:
                skills = json.loads(skills_json)
                
                # Validate and clean
                cleaned_skills = []
                stopwords = {'experience', 'years', 'team', 'work', 'skills', 'required', 
                            'preferred', 'must', 'knowledge', 'strong', 'good', 'excellent'}
                
                for skill in skills:
                    if isinstance(skill, str):
                        skill_clean = skill.strip()
                        
                        
                        # Remove items that are too short, too long, or stopwords
                        if (2 < len(skill_clean) < 50 and 
                            skill_clean.lower() not in stopwords and
                            not skill_clean.lower().startswith('experience in')):
                            cleaned_skills.append(skill_clean)
                
                from analytics.skill_normalizer import normalize_skill_list

                cleaned_skills = normalize_skill_list(cleaned_skills)

                return cleaned_skills[:25]
                
            except json.JSONDecodeError:
                # Try fixing common JSON issues
                skills_json_fixed = skills_json.replace("'", '"')  # Single to double quotes
                try:
                    skills = json.loads(skills_json_fixed)
                    cleaned_skills = [s.strip() for s in skills if isinstance(s, str) and len(s) > 2]
                    
                    from analytics.skill_normalizer import normalize_skill_list

                    cleaned_skills = normalize_skill_list(cleaned_skills)

                    return cleaned_skills[:25]
                except:
                    pass
        
        # If we get here, extraction failed
        return []
            
    except Exception as e:
        error_msg = str(e).lower()
    
        if '429' in error_msg or 'rate limit' in error_msg:
            print("Daily limit reached → skipping remaining...")
            return [] # retry
    
        print(f"Error: {str(e)[:100]}")
        return []


def extract_skills_batch(jobs):
    """
    Extract skills from multiple jobs with rate limiting and progress tracking
    """
    total = len(jobs)
    print(f"Starting AI skill extraction with Groq Llama 3.1 70B...")
    print(f"Processing {total} jobs...")
    
    successful = 0
    failed = 0
    failed_jobs = []
    
    for idx, job in enumerate(jobs, 1):
        description = job.get('description', '')
        
        # Extract skills
        skills = extract_skills_from_description(job)
        job['skills'] = skills
        
        if skills:
            successful += 1
        else:
            failed += 1
            failed_jobs.append({
                'title': job.get('title', 'N/A')[:40],
                'company': job.get('company', 'N/A')[:30],
                'desc_length': len(description) if description else 0
            })
        
        # Rate limiting: 2 seconds between calls (30 req/min limit)
        time.sleep(3)
        
        # Progress indicator
        if idx % 5 == 0 or idx == total:
            print(f"Progress: {idx}/{total} |  Success: {successful} | Failed: {failed}")
    
    success_rate = (successful / total * 100) if total > 0 else 0
    print(f" Extraction complete: {successful}/{total} ({success_rate:.1f}% success)")
    
    # Show failures if there are any (but not too many)
    if failed_jobs and len(failed_jobs) <= 8:
        print(f"\nJobs without skills ({len(failed_jobs)}):")
        for job in failed_jobs:
            reason = "too short" if job['desc_length'] < 50 else "no tech skills found"
            print(f"   - {job['title']} @ {job['company']} ({reason})")
    
    return jobs


# Test function
if __name__ == "__main__":
    test_description = """
    <p><strong>Flutter Developer Position</strong></p>
    
    We are looking for an experienced Flutter developer.
    
    Required Skills:
    - 3+ years with Flutter and Dart
    - Experience with Firebase
    - Knowledge of REST APIs
    - Git version control
    - State management (Provider, Bloc)
    
    Nice to have:
    - GraphQL
    - CI/CD experience
    """
    
    print("=" * 70)
    print("TESTING GROQ LLAMA 3.1 70B - ENHANCED VERSION")
    print("=" * 70)
    
    skills = extract_skills_from_description(test_description)
    
    print(f"\nExtracted {len(skills)} skills:")
    print("-" * 70)
    for i, skill in enumerate(skills, 1):
        print(f"{i:2}. {skill}")
    
    print("\n" + "=" * 70)