from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(
    MONGODB_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000
)

db = client["skillpulse"]

users_collection = db["users"]
jobs_collection = db["jobs"]
skills_collection = db["skills"]
trends_collection = db["trends"]
logs_collection = db["collection_logs"]
user_paths_collection = db['user_paths']
users_collection = db['users']
#Add collection_logs collection
collection_logs_collection = db['collection_logs']
def test_connection():
    try:
        client.admin.command("ping")
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()