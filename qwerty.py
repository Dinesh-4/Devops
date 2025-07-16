# test_mongo_connection.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = "mongodb+srv://kannanb2745:kannanb2745@kannan.8bbghpx.mongodb.net/"

def test_mongodb_connection():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection on a request as the connect=True parameter of MongoClient seems not always reliable.
        print("✅ Successfully connected to MongoDB Atlas!")
    except ConnectionFailure as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    test_mongodb_connection()
