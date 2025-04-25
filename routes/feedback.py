
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from models.feedback import FeedbackCreate, FeedbackInDB
from models.user import User
from core.database import get_collection
from utils.jwt import get_current_user
from utils.helper import generate_response, generate_id
from utils.logger import setup_logger, log_request

router = APIRouter()
logger = setup_logger("feedback")

@router.post("/submit", response_model=dict)
async def submit_feedback(
    feedback: FeedbackCreate,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Submit user feedback"""
    # Log request
    log_request(logger, feedback.dict(), current_user.id if current_user else None)
    
    # Create feedback entry
    feedback_id = generate_id("fb_")
    feedback_db = FeedbackInDB(
        id=feedback_id,
        type=feedback.type,
        message=feedback.message,
        email=feedback.email,
        user_id=current_user.id if current_user else None
    )
    
    # Save to database
    feedback_collection = get_collection("feedback")
    await feedback_collection.insert_one(feedback_db.dict())
    
    return generate_response(
        data={"feedback_id": feedback_id},
        message="Feedback submitted successfully"
    )
