from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")  # e.g., "mongodb://localhost:27017"
DB_NAME = "ci_cd_logs"
COLLECTION_NAME = "summaries"

def fetch_recent_summaries(hours=2):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent_logs = collection.find({"timestamp": {"$gte": cutoff}}).sort("timestamp", -1)

    print(f"\n🕒 Showing commits from last {hours} hour(s):\n")
    for log in recent_logs:
        print("🔹 Commit SHA:", log["commit_sha"])
        print("🕓 Time:", log["timestamp"])
        print("📂 Branch:", log["branch"])
        print("✅ Status:", log["status"])
        # print("📋 Summary:\n" + log["summary"])
        print("\n")
        print("-" * 60)
        print("\n")

if __name__ == "__main__":
    fetch_recent_summaries(hours=2)

