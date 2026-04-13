"""
Master Job Collector (Improved - Dynamic Roles)
"""
import time
import sys
import os
from datetime import datetime
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# Automatically find the absolute path to the 'src' folder
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

from src.collectors.adzuna_collector import fetch_adzuna_jobs
from src.collectors.remotive_collector import collect_remotive_jobs
from src.collectors.jsearch_collector import collect_jsearch_jobs
from src.database import jobs_collection, collection_logs_collection

# ----------------------------
# 🔥 ROLE EXPANSION (AI)
# ----------------------------
def expand_role(role):
    prompt = f"""
Expand this tech job role into 5 related job titles.

Role: {role}

Only return job titles (one per line).
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100
        )
        text = response.choices[0].message.content
        return [line.strip() for line in text.split("\n") if line.strip()]
    except:
        return [role]  # fallback

# ----------------------------
# 🔁 DEDUPLICATION
# ----------------------------
def deduplicate_jobs(jobs):
    seen = set()
    unique_jobs = []

    for job in jobs:
        key = (job.get('title', '').lower().strip(), job.get('company', '').lower().strip())

        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    print(f"\nDeduplication: Removed {len(jobs) - len(unique_jobs)} duplicates")
    return unique_jobs

# ----------------------------
# 💾 SAVE
# ----------------------------
def save_jobs_batch(jobs):
    saved = 0
    duplicates = 0

    for job in jobs:
        existing = jobs_collection.find_one({
            'title': job.get('title', ''),
            'company': job.get('company', '')
        })

        if existing:
            duplicates += 1
        else:
            jobs_collection.insert_one(job)
            saved += 1

    print(f"Saved to DB: {saved} | Already existed: {duplicates}")
    return saved

# ----------------------------
# 🚀 MAIN FUNCTION
# ----------------------------
def collect_all_jobs():
    print("=" * 70)
    print("SKILLPULSE - DYNAMIC JOB COLLECTION")
    print("=" * 70)

    # ----------------------------
    # 🌟 DYNAMIC ROLE GENERATION
    # ----------------------------
    base_domains = [
        "Software Engineering",
        "Data Science and Analytics",
        "Cloud Infrastructure and DevOps",
        "Artificial Intelligence and Machine Learning",
        "QA Testing and Automation",
        "UI/UX Design",
        "Cybersecurity",
        "Blockchain and Web3"
    ]

    print("\n🧠 Asking AI to generate specific job titles from domains...")

    all_target_roles = []
    
    for domain in base_domains:
        print(f"Expanding domain: {domain}...")
        specific_roles = expand_role(domain)
        
        for role in specific_roles:
            # Clean up any bullet points or numbers
            clean_role = role.replace("- ", "").replace("* ", "").strip()
            if len(clean_role) > 2 and clean_role[0].isdigit() and clean_role[1] in ['.', ')']:
                clean_role = clean_role[2:].strip()
                
            if clean_role and clean_role not in all_target_roles:
                all_target_roles.append(clean_role)
                print(f"   ✓ Added: {clean_role}")

    print(f"\n🎯 Total unique roles to scrape: {len(all_target_roles)}")

    # ----------------------------
    # 📥 JOB COLLECTION
    # ----------------------------
    all_jobs = []
    sources = {'adzuna': 0, 'remotive': 0, 'jsearch': 0}

    print("\nStarting collection across APIs...")

    # 1. Fetch Adzuna
    print("\n➡️ Fetching from Adzuna...")
    for role in all_target_roles:
        adzuna_jobs = fetch_adzuna_jobs(what=role, results_per_page=1)
        if adzuna_jobs:
            sources['adzuna'] += len(adzuna_jobs)
            all_jobs.extend(adzuna_jobs)
        time.sleep(1) # Be nice to the API

    # 2. Fetch JSearch
    print("\n➡️ Fetching from JSearch...")
    jsearch_queries = [f"{role} India" for role in all_target_roles]
    jsearch_jobs = collect_jsearch_jobs(queries=jsearch_queries, max_per_query=1)
    if jsearch_jobs:
        sources['jsearch'] += len(jsearch_jobs)
        all_jobs.extend(jsearch_jobs)

    # 3. Fetch Remotive
    print("\n➡️ Fetching from Remotive...")
    remotive_jobs = collect_remotive_jobs(limit=5)
    if remotive_jobs:
        sources['remotive'] += len(remotive_jobs)
        all_jobs.extend(remotive_jobs)

    # ----------------------------
    # SUMMARY & SAVING
    # ----------------------------
    print("\n" + "=" * 70)
    print("COLLECTION SUMMARY")
    print("=" * 70)

    print(f"Adzuna:   {sources['adzuna']}")
    print(f"Remotive: {sources['remotive']}")
    print(f"JSearch:  {sources['jsearch']}")
    print(f"Total fetched: {len(all_jobs)}")

    if len(all_jobs) > 0:
        unique_jobs = deduplicate_jobs(all_jobs)
        print(f"After dedup: {len(unique_jobs)}")

        print("\nSaving to DB...")
        saved = save_jobs_batch(unique_jobs)
        
        collection_logs_collection.insert_one({
            'timestamp': datetime.now(),
            'totalFetched': len(all_jobs),
            'afterDedup': len(unique_jobs),
            'saved': saved,
            'sources': sources,
            'status': 'success'
        })
        print(f"New jobs added: {saved}")
    else:
        print("No jobs collected to save.")
        
    print(f"Total jobs in DB: {jobs_collection.count_documents({})}")

# ----------------------------
if __name__ == "__main__":
    collect_all_jobs()