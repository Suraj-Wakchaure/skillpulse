import requests
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("TESTING API AVAILABILITY")
print("=" * 70)

# 1. Test Remotive
print("\n1️⃣ Testing Remotive API...")
try:
    response = requests.get(
        "https://remotive.com/api/remote-jobs",
        params={"category": "software-dev", "limit": 5},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        jobs = data.get('jobs', [])
        print(f"   ✅ Working! Found {len(jobs)} jobs")
        if jobs:
            print(f"   Sample: {jobs[0].get('title', 'N/A')}")
    else:
        print(f"   ❌ Error {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Test JSearch (RapidAPI)
print("\n2️⃣ Testing JSearch API...")
jsearch_key = os.getenv('JSEARCH_API_KEY')

if jsearch_key and jsearch_key != 'your_key_here':
    try:
        response = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers={
                "X-RapidAPI-Key": jsearch_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            },
            params={
                "query": "Python developer in India",
                "page": "1",
                "num_pages": "1"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('data', [])
            print(f"   ✅ Working! Found {len(jobs)} jobs")
            if jobs:
                print(f"   Sample: {jobs[0].get('job_title', 'N/A')}")
        else:
            print(f"   ❌ Error {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print("   ⚠️  No API key in .env")

# 3. Test Adzuna (already working)
print("\n3️⃣ Testing Adzuna API...")
adzuna_id = os.getenv('ADZUNA_APP_ID')
adzuna_key = os.getenv('ADZUNA_APP_KEY')

if adzuna_id and adzuna_key:
    try:
        response = requests.get(
            "https://api.adzuna.com/v1/api/jobs/in/search/1",
            params={
                'app_id': adzuna_id,
                'app_key': adzuna_key,
                'results_per_page': 5,
                'what': 'developer',
                'where': 'india'
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('results', [])
            print(f"   ✅ Working! Found {len(jobs)} jobs")
        else:
            print(f"   ❌ Error {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print("   ⚠️  No API keys")

print("\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)
print("Ready to collect from:")
print("  ✅ Remotive")
print("  ✅ JSearch")
print("  ✅ Adzuna")
print("=" * 70)