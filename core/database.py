from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging
import os
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

class Settings:
    MONGO_URI = os.getenv("MONGO_URI")  # Pastikan variabel ini ada di .env
    DATABASE_NAME = "scryptex"

settings = Settings()

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @staticmethod
    async def connect():
        """Create database connection."""
        try:
            Database.client = AsyncIOMotorClient(settings.MONGO_URI)
            Database.db = Database.client[settings.DATABASE_NAME]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            Database.db = None
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e

    @staticmethod
    async def disconnect():
        """Close database connection."""
        if Database.client:
            Database.client.close()
            logger.info("Closed MongoDB connection")

# Alias untuk mempermudah impor
db = Database.db

def get_collection(collection_name: str):
    """Get a specific collection from the database."""
    if Database.db is None:
        raise ValueError("Database connection is not initialized")
    return Database.db[collection_name]

router = APIRouter()

async def create_user_with_referral(payload: dict):
    """
    Membuat pengguna baru dengan referral code.
    """
    username = payload.get("username")
    email = payload.get("email")
    referred_by = payload.get("ref")

    # Validasi input
    if not username or not email:
        raise ValueError("Username and email are required")

    # Cek apakah email sudah terdaftar
    existing_user = await db["waitlist"].find_one({"email": email})
    if existing_user:
        raise ValueError("Email already registered")

    # Buat referral code unik
    referral_code = f"{username[:3]}{len(username)}"

    # Simpan ke database
    user = {
        "username": username,
        "email": email,
        "referral_code": referral_code,
        "referred_by": referred_by,
        "referral_count": 0,
        "reward_pending_tex": 0,
    }
    result = await db["waitlist"].insert_one(user)

    # Ambil data pengguna yang baru saja disimpan
    user["_id"] = result.inserted_id
    return user

async def get_referrer_by_code(referral_code: str):
    """
    Memeriksa apakah kode referral valid dan mengembalikan data pengguna yang merujuk.
    """
    collection = get_collection("waitlist")
    referrer = await collection.find_one({"referral_code": referral_code})
    return referrer

