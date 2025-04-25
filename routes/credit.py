
from fastapi import APIRouter, HTTPException, Path, Query, Depends, status
from typing import List, Optional

from models.credit import CreditTopUpRequest, CreditLog, CreditBalance
from models.user import User
from utils.helper import generate_response, generate_id
from utils.jwt import get_current_user
from core.database import get_collection
from utils.logger import setup_logger, log_request

router = APIRouter(prefix="/credit")
logger = setup_logger("credit")

@router.get("/status", response_model=dict)
async def get_credit_status(current_user: User = Depends(get_current_user)):
    """
    Get user's current credit balance and history
    """
    # Log request
    log_request(logger, {}, current_user.id)
    
    # Get credit balance from database
    credit_collection = get_collection("credit_balances")
    credit_balance = await credit_collection.find_one({"user_id": current_user.id})
    
    if not credit_balance:
        # Create initial balance if it doesn't exist
        credit_balance = {
            "user_id": current_user.id,
            "balance": 5.0,  # Default 5 credits for new users
            "last_updated": datetime.utcnow(),
            "lifetime_earned": 5.0,
            "lifetime_spent": 0.0
        }
        await credit_collection.insert_one(credit_balance)
    
    # Get recent credit logs
    logs_collection = get_collection("credit_logs")
    recent_logs_cursor = logs_collection.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1).limit(5)
    
    recent_logs = []
    async for log in recent_logs_cursor:
        recent_logs.append({
            "action": log["action"],
            "amount": log["amount"],
            "description": log["description"],
            "created_at": log["created_at"].isoformat()
        })
    
    return generate_response(
        data={
            "balance": credit_balance["balance"],
            "lifetime_earned": credit_balance["lifetime_earned"],
            "lifetime_spent": credit_balance["lifetime_spent"],
            "recent_logs": recent_logs
        },
        message="Credit status retrieved successfully"
    )

@router.post("/use", response_model=dict)
async def use_credit(
    amount: float = Query(..., description="Amount of credits to use"),
    action: str = Query(..., description="Action requiring credits (analyze, farming, twitter)"),
    related_entity: Optional[str] = Query(None, description="ID of related entity (project_id, etc.)"),
    current_user: User = Depends(get_current_user)
):
    """
    Use credits for a specific action
    """
    # Log request
    log_request(logger, {"amount": amount, "action": action}, current_user.id)
    
    # Get credit balance from database
    credit_collection = get_collection("credit_balances")
    credit_balance = await credit_collection.find_one({"user_id": current_user.id})
    
    if not credit_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No credit balance found for user"
        )
    
    # Check if user has enough credits
    if credit_balance["balance"] < amount:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. You have {credit_balance['balance']} but need {amount}"
        )
    
    # Update credit balance
    new_balance = credit_balance["balance"] - amount
    lifetime_spent = credit_balance["lifetime_spent"] + amount
    
    await credit_collection.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "balance": new_balance, 
            "lifetime_spent": lifetime_spent,
            "last_updated": datetime.utcnow()
        }}
    )
    
    # Log credit usage
    logs_collection = get_collection("credit_logs")
    action_descriptions = {
        "analyze": "Project analysis",
        "farming": "Automated farming",
        "twitter": "Twitter automation"
    }
    
    credit_log = {
        "user_id": current_user.id,
        "action": "use",
        "amount": amount,
        "description": action_descriptions.get(action, action),
        "related_entity": related_entity,
        "created_at": datetime.utcnow()
    }
    
    await logs_collection.insert_one(credit_log)
    
    # Also log to general logs collection
    logs_general = get_collection("logs")
    await logs_general.insert_one({
        "user_id": current_user.id,
        "action": f"credit_use_{action}",
        "metadata": {
            "amount": amount,
            "related_entity": related_entity
        },
        "timestamp": datetime.utcnow()
    })
    
    return generate_response(
        data={
            "remaining_credits": new_balance,
            "action": action,
            "amount_used": amount
        },
        message="Credits used successfully"
    )

@router.post("/topup-request", response_model=dict)
async def request_credit_topup(
    amount: float = Query(..., description="Amount to topup in USDT"),
    payment_method: str = Query(..., description="Payment method (crypto, fiat)"),
    wallet_address: Optional[str] = Query(None, description="Wallet address for crypto payments"),
    current_user: User = Depends(get_current_user)
):
    """
    Request a credit top-up
    """
    # Log request
    log_request(logger, {
        "amount": amount, 
        "payment_method": payment_method,
        "wallet_address": wallet_address
    }, current_user.id)
    
    # Validate request
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )
    
    if payment_method not in ["crypto", "fiat"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method must be either 'crypto' or 'fiat'"
        )
    
    if payment_method == "crypto" and not wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet address is required for crypto payments"
        )
    
    # Create top-up request
    topup_collection = get_collection("topup_requests")
    topup_id = generate_id("topup_")
    
    topup_request = {
        "id": topup_id,
        "user_id": current_user.id,
        "amount": amount,
        "currency": "USDT",
        "payment_method": payment_method,
        "wallet_address": wallet_address,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await topup_collection.insert_one(topup_request)
    
    # Generate payment instructions
    payment_instructions = {
        "id": topup_id,
        "amount": amount,
        "currency": "USDT"
    }
    
    if payment_method == "crypto":
        payment_instructions["wallet_address"] = "0x9876543210fedcba9876543210fedcba98765432"  # Example Scryptex wallet
        payment_instructions["network"] = "Ethereum (ERC-20)"
        payment_instructions["token"] = "USDT"
    else:  # fiat
        payment_instructions["bank_name"] = "Scryptex Bank"
        payment_instructions["account_name"] = "Scryptex Ltd."
        payment_instructions["reference"] = f"SCRYX-{topup_id}"
    
    return generate_response(
        data={
            "topup_id": topup_id,
            "instructions": payment_instructions,
            "status": "pending"
        },
        message="Top-up request created successfully"
    )

@router.post("/verify-payment", response_model=dict)
async def verify_payment(
    topup_id: str = Query(..., description="Top-up request ID"),
    transaction_hash: Optional[str] = Query(None, description="Transaction hash for crypto payments"),
    current_user: User = Depends(get_current_user)
):
    """
    Verify a payment for a top-up request
    """
    # This endpoint would normally connect to a blockchain node or payment processor
    # Here we'll simulate the verification process
    
    # Log request
    log_request(logger, {"topup_id": topup_id, "tx_hash": transaction_hash}, current_user.id)
    
    # Get top-up request
    topup_collection = get_collection("topup_requests")
    topup = await topup_collection.find_one({"id": topup_id, "user_id": current_user.id})
    
    if not topup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Top-up request not found"
        )
    
    if topup["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Top-up is already {topup['status']}"
        )
    
    # Simulate payment verification
    # In a real system, this would verify the transaction on the blockchain
    # or check the payment processor's API
    verification_success = True
    
    if verification_success:
        # Update top-up status
        await topup_collection.update_one(
            {"id": topup_id},
            {"$set": {
                "status": "approved",
                "transaction_hash": transaction_hash,
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Calculate credit amount (conversion rate simulation)
        credit_amount = topup["amount"] * 10  # Example: 1 USDT = 10 credits
        
        # Update user's credit balance
        credit_collection = get_collection("credit_balances")
        credit_balance = await credit_collection.find_one({"user_id": current_user.id})
        
        if not credit_balance:
            credit_balance = {
                "user_id": current_user.id,
                "balance": credit_amount,
                "lifetime_earned": credit_amount,
                "lifetime_spent": 0.0,
                "last_updated": datetime.utcnow()
            }
            await credit_collection.insert_one(credit_balance)
        else:
            new_balance = credit_balance["balance"] + credit_amount
            lifetime_earned = credit_balance["lifetime_earned"] + credit_amount
            
            await credit_collection.update_one(
                {"user_id": current_user.id},
                {"$set": {
                    "balance": new_balance,
                    "lifetime_earned": lifetime_earned,
                    "last_updated": datetime.utcnow()
                }}
            )
        
        # Log credit top-up
        logs_collection = get_collection("credit_logs")
        credit_log = {
            "user_id": current_user.id,
            "action": "topup",
            "amount": credit_amount,
            "description": f"Top-up via {topup['payment_method']}",
            "related_entity": topup_id,
            "created_at": datetime.utcnow()
        }
        await logs_collection.insert_one(credit_log)
        
        # Also log to general logs collection
        logs_general = get_collection("logs")
        await logs_general.insert_one({
            "user_id": current_user.id,
            "action": "credit_topup",
            "metadata": {
                "amount": credit_amount,
                "payment_method": topup["payment_method"],
                "topup_id": topup_id
            },
            "timestamp": datetime.utcnow()
        })
        
        return generate_response(
            data={
                "topup_id": topup_id,
                "status": "approved",
                "credits_added": credit_amount,
                "new_balance": new_balance
            },
            message="Payment verified and credits added successfully"
        )
    else:
        # Update top-up status
        await topup_collection.update_one(
            {"id": topup_id},
            {"$set": {
                "status": "failed",
                "updated_at": datetime.utcnow()
            }}
        )
        
        return generate_response(
            data={
                "topup_id": topup_id,
                "status": "failed"
            },
            message="Payment verification failed",
            success=False
        )

# Add import for datetime at the top
from datetime import datetime
