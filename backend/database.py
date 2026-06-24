import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/edtech")

# Initialize client and database at module level
# Added TLS and timeout parameters to prevent SSL handshake/timeout errors on Render
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000
)

db = client["edtech"]

# Export collection references — all other modules import these directly
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
