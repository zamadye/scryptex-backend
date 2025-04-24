import logging
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from models.waitlist import WaitlistUser
from services.referral_logic import create_user_with_referral, update_referral_rewards, get_referrer_by_code
from core.database import db

router = APIRouter(prefix="/api/waitlist", tags=["Waitlist"])

def custom_jsonable_encoder(data):
    if isinstance(data, ObjectId):
        return str(data)
    return jsonable_encoder(data)

@router.post("")
async def join_waitlist(payload: dict):
    """
    Endpoint untuk menambahkan pengguna ke waitlist dan memberikan reward jika ada referral.
    """
    try:
        # Validasi payload
        if not payload.get("username") or not payload.get("email"):
            raise HTTPException(status_code=400, detail="Username and email are required")

        # Validasi kode referral
        ref = payload.get("ref")
        if ref:
            referrer = await get_referrer_by_code(ref)
            if not referrer:
                raise HTTPException(status_code=400, detail="Invalid referral code")

        # Buat pengguna baru dengan referral
        user = await create_user_with_referral(payload)
        logging.info(f"User data: {user}")

        # Jika pengguna dirujuk oleh orang lain, tambahkan reward ke referral
        if ref:
            await update_referral_rewards(ref)

        return {
            "status": "success",
            "data": {
                "username": user["username"],
                "referral_code": user["referral_code"],
                "reward_pending_tex": user["reward_pending_tex"]
            }
        }
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{code}")
async def get_referral_data(code: str):
    """
    Endpoint untuk mendapatkan data referral berdasarkan kode referral.
    """
    try:
        user = await db["waitlist"].find_one({"referral_code": code})
        if not user:
            raise HTTPException(status_code=404, detail="Referral code not found")

        # Konversi ObjectId ke string
        user["_id"] = str(user["_id"])

        return {
            "username": user["username"],
            "referral_code": user["referral_code"],
            "referral_count": user["referral_count"],
            "reward_pending_tex": user["reward_pending_tex"]
        }
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
