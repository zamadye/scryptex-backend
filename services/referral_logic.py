import random
import string
from datetime import datetime
from bson import ObjectId
from core.database import get_collection

async def generate_referral_code(length=6):
    """
    Membuat kode referral unik dengan panjang tertentu.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def create_user_with_referral(payload: dict):
    """
    Membuat pengguna baru dengan referral code dan menyimpan ke database.
    """
    collection = get_collection("waitlist")

    username = payload.get("username")
    email = payload.get("email")
    referred_by = payload.get("ref")

    # Validasi input
    if not username or not email:
        raise ValueError("Username and email are required")

    # Cek apakah email sudah terdaftar
    existing_user = await collection.find_one({"email": email})
    if existing_user:
        raise ValueError("Email already registered")

    # Buat referral code unik
    referral_code = await generate_referral_code()

    # Simpan ke database
    user = {
        "username": username,
        "email": email,
        "referral_code": referral_code,
        "referred_by": referred_by,
        "referral_count": 0,
        "reward_pending_tex": 0,
        "created_at": datetime.utcnow(),
    }
    result = await collection.insert_one(user)

    # Ambil data pengguna yang baru saja disimpan
    user["_id"] = str(result.inserted_id)  # Konversi ObjectId ke string
    return user

async def update_referral_rewards(referral_code: str):
    """
    Menambahkan reward TEX ke pengguna yang merujuk.
    """
    collection = get_collection("waitlist")

    # Cari pengguna berdasarkan referral_code
    referrer = await collection.find_one({"referral_code": referral_code})
    if not referrer:
        raise ValueError("Referrer not found")

    # Tambahkan reward TEX (misalnya 5 TEX per referral)
    reward_amount = 5
    await collection.update_one(
        {"referral_code": referral_code},
        {
            "$inc": {
                "referral_count": 1,
                "reward_pending_tex": reward_amount
            }
        }
    )

async def get_referrer_by_code(referral_code: str):
    """
    Memeriksa apakah kode referral valid dan mengembalikan data pengguna yang merujuk.
    """
    collection = get_collection("waitlist")  # Ambil koleksi "waitlist"
    referrer = await collection.find_one({"referral_code": referral_code})
    return referrer

