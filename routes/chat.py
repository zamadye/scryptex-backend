
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List

from models.chat import ChatMessageCreate, ChatThread, ChatMessage
from models.user import User
from core.database import get_collection
from utils.jwt import get_current_user
from utils.helper import generate_response, generate_id
from utils.logger import setup_logger, log_request

router = APIRouter()
logger = setup_logger("chat")

@router.post("/send", response_model=dict)
async def send_message(
    message: ChatMessageCreate,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Send a chat message and get a response"""
    # Log request
    log_request(logger, message.dict(), current_user.id if current_user else None)
    
    chat_collection = get_collection("chat_threads")
    thread_id = message.thread_id
    
    # If thread_id is provided, verify it exists
    if thread_id:
        thread = await chat_collection.find_one({"id": thread_id})
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat thread not found"
            )
    # Otherwise create a new thread
    else:
        thread_id = generate_id("chat_")
        thread = ChatThread(
            id=thread_id,
            user_id=current_user.id if current_user else None,
        )
        await chat_collection.insert_one(thread.dict())
    
    # Add user message to thread
    user_message = ChatMessage(
        content=message.content,
        sender="user"
    )
    
    # Simulate bot response
    bot_responses = {
        "help": "How can I assist you with Scryptex today?",
        "airdrop": "Our airdrop analyzer helps you identify legitimate airdrops and avoid scams.",
        "farming": "Scryptex can help you identify the best farming opportunities across different chains.",
        "price": "I can't provide real-time price data, but our analysis tools can help with tokenomics research.",
        "default": "Thanks for your message! Our team will review and get back to you soon."
    }
    
    # Simple keyword matching for demo
    bot_response_text = bot_responses["default"]
    for keyword, response in bot_responses.items():
        if keyword in message.content.lower():
            bot_response_text = response
            break
    
    bot_message = ChatMessage(
        content=bot_response_text,
        sender="bot"
    )
    
    # Update thread with both messages
    await chat_collection.update_one(
        {"id": thread_id},
        {
            "$push": {"messages": {"$each": [user_message.dict(), bot_message.dict()]}},
            "$set": {"updated_at": user_message.timestamp}
        }
    )
    
    return generate_response(
        data={
            "thread_id": thread_id,
            "response": bot_message.dict()
        },
        message="Message sent successfully"
    )

@router.get("/threads", response_model=dict)
async def get_threads(current_user: User = Depends(get_current_user)):
    """Get all chat threads for the current user"""
    chat_collection = get_collection("chat_threads")
    
    # Find all threads for this user
    threads_cursor = chat_collection.find({"user_id": current_user.id})
    threads = [ChatThread(**thread) for thread in await threads_cursor.to_list(length=100)]
    
    return generate_response(
        data={"threads": [thread.dict() for thread in threads]},
        message="Chat threads retrieved successfully"
    )

@router.get("/thread/{thread_id}", response_model=dict)
async def get_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat thread"""
    chat_collection = get_collection("chat_threads")
    
    # Find thread
    thread = await chat_collection.find_one({"id": thread_id})
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat thread not found"
        )
    
    # Check permissions
    if thread.get("user_id") and thread["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this chat thread"
        )
    
    return generate_response(
        data={"thread": ChatThread(**thread).dict()},
        message="Chat thread retrieved successfully"
    )
