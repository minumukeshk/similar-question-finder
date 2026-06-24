from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(
    MONGO_URI,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=30000
)

db = client["edtech"]
users_collection = db["users"]
questions_collection = db["questions"]


async def connect_db() -> None:
    """Verify the MongoDB connection is alive and ensure indexes."""
    # Ping to confirm Atlas is reachable
    await client.admin.command("ping")
    print("MongoDB connected successfully")

    # Ensure indexes for fast lookups
    await users_collection.create_index("email", unique=True)
    await questions_collection.create_index("user_id")
    await questions_collection.create_index("tag")
    print("[DB] Indexes ensured on users.email, questions.user_id, questions.tag")


async def close_db() -> None:
    """Close the MongoDB client connection."""
    client.close()
    print("[DB] MongoDB connection closed.")
