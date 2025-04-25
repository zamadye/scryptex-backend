
from fastapi import APIRouter, HTTPException, Path, Query, Depends, status
from typing import List, Optional
import asyncio
import random
from datetime import datetime, timedelta

from schemas.farming import FarmingStartRequest, FarmingAnalyzeRequest, FarmingProject, FarmingTask
from models.user import User
from models.farming import FarmingLog
from utils.helper import generate_response, generate_id
from utils.jwt import get_current_user
from core.database import get_collection
from utils.logger import setup_logger, log_request

router = APIRouter(prefix="/farming")
logger = setup_logger("farming")

@router.post("/analyze", response_model=dict)
async def analyze_farming_tasks(
    request: FarmingAnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze farming tasks for a specific project and chain
    """
    # Log request
    log_request(logger, request.dict(), current_user.id)
    
    # Check if user has enough credits
    credit_collection = get_collection("credit_balances")
    credit_balance = await credit_collection.find_one({"user_id": current_user.id})
    
    if not credit_balance or credit_balance["balance"] < 1:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits to analyze farming tasks"
        )
    
    # Deduct credits (1 credit for analysis)
    await credit_collection.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "balance": credit_balance["balance"] - 1,
            "lifetime_spent": credit_balance["lifetime_spent"] + 1,
            "last_updated": datetime.utcnow()
        }}
    )
    
    # Log credit usage
    logs_collection = get_collection("credit_logs")
    credit_log = {
        "user_id": current_user.id,
        "action": "use",
        "amount": 1.0,
        "description": f"Farming analysis for {request.project_name} on {request.chain}",
        "created_at": datetime.utcnow()
    }
    await logs_collection.insert_one(credit_log)
    
    # Generate farming tasks based on chain
    tasks = []
    
    # Different task templates based on chain
    chain_tasks = {
        "zkSync": [
            {"name": "Mint NFT", "type": "mint", "required": True, "gas_cost_estimate": 0.005},
            {"name": "Swap Token", "type": "swap", "required": True, "gas_cost_estimate": 0.003},
            {"name": "Add Liquidity", "type": "liquidity", "required": False, "gas_cost_estimate": 0.008}
        ],
        "Sui": [
            {"name": "Mint Object", "type": "mint", "required": True, "gas_cost_estimate": 0.001},
            {"name": "Swap SUI", "type": "swap", "required": True, "gas_cost_estimate": 0.002},
        ],
        "Scroll": [
            {"name": "Bridge ETH", "type": "bridge", "required": True, "gas_cost_estimate": 0.007},
            {"name": "Swap Token", "type": "swap", "required": True, "gas_cost_estimate": 0.004},
            {"name": "Deploy Contract", "type": "contract", "required": False, "gas_cost_estimate": 0.01}
        ]
    }
    
    # Get tasks for the selected chain, or use default tasks
    selected_tasks = chain_tasks.get(request.chain, [
        {"name": "Generic Task 1", "type": "swap", "required": True, "gas_cost_estimate": 0.003},
        {"name": "Generic Task 2", "type": "mint", "required": True, "gas_cost_estimate": 0.004}
    ])
    
    # Create tasks with project-specific names
    for task in selected_tasks:
        task_name = task["name"]
        if "swap" in task["type"].lower():
            task_name = f"Swap on {request.project_name} DEX"
        elif "mint" in task["type"].lower():
            task_name = f"Mint {request.project_name} NFT"
        
        tasks.append({
            "name": task_name,
            "type": task["type"],
            "required": task["required"],
            "gas_cost_estimate": task["gas_cost_estimate"]
        })
    
    # Create project ID
    project_id = generate_id("farm_")
    
    # Save project to database
    projects_collection = get_collection("farming_projects")
    
    project = {
        "id": project_id,
        "user_id": current_user.id,
        "project_name": request.project_name,
        "chain": request.chain,
        "wallet_address": request.wallet_address,
        "tasks": tasks,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await projects_collection.insert_one(project)
    
    # Log to general logs
    logs_general = get_collection("logs")
    await logs_general.insert_one({
        "user_id": current_user.id,
        "action": "farming_analyze",
        "metadata": {
            "project_id": project_id,
            "project_name": request.project_name,
            "chain": request.chain
        },
        "timestamp": datetime.utcnow()
    })
    
    return generate_response(
        data={
            "project_id": project_id,
            "name": request.project_name,
            "chain": request.chain,
            "tasks": tasks
        },
        message="Farming tasks analyzed successfully"
    )

@router.post("/start", response_model=dict)
async def start_farming(
    request: FarmingStartRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Start automated farming of tasks
    """
    # Log request
    log_request(logger, request.dict(), current_user.id)
    
    # Get project from database
    projects_collection = get_collection("farming_projects")
    project = await projects_collection.find_one({"id": request.project_id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {request.project_id} not found"
        )
    
    # Check if user owns the project
    if project["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to farm this project"
        )
    
    # Check if farming is already in progress
    if project["status"] == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farming already in progress for this project"
        )
    
    # Check if user has enough credits
    credit_collection = get_collection("credit_balances")
    credit_balance = await credit_collection.find_one({"user_id": current_user.id})
    
    if not credit_balance or credit_balance["balance"] < 2:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits to start farming (requires 2 credits)"
        )
    
    # Deduct credits (2 credits for farming)
    await credit_collection.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "balance": credit_balance["balance"] - 2,
            "lifetime_spent": credit_balance["lifetime_spent"] + 2,
            "last_updated": datetime.utcnow()
        }}
    )
    
    # Log credit usage
    logs_collection = get_collection("credit_logs")
    credit_log = {
        "user_id": current_user.id,
        "action": "use",
        "amount": 2.0,
        "description": f"Start farming for {project['project_name']} on {project['chain']}",
        "related_entity": request.project_id,
        "created_at": datetime.utcnow()
    }
    await logs_collection.insert_one(credit_log)
    
    # Update project status
    await projects_collection.update_one(
        {"id": request.project_id},
        {"$set": {
            "status": "running",
            "wallet_address": request.wallet_address or project.get("wallet_address"),
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Set up farming logs
    farming_logs_collection = get_collection("farming_logs")
    
    # Log start
    start_log = {
        "project_id": request.project_id,
        "user_id": current_user.id,
        "message": f"Starting auto-farming on {project['chain']} for {project['project_name']}",
        "level": "info",
        "created_at": datetime.utcnow()
    }
    await farming_logs_collection.insert_one(start_log)
    
    # Log to general logs
    logs_general = get_collection("logs")
    await logs_general.insert_one({
        "user_id": current_user.id,
        "action": "farming_start",
        "metadata": {
            "project_id": request.project_id,
            "project_name": project["project_name"],
            "chain": project["chain"]
        },
        "timestamp": datetime.utcnow()
    })
    
    # Get task subset if specified
    task_subset = []
    if request.tasks and len(request.tasks) > 0:
        for task in project["tasks"]:
            if task["name"] in request.tasks:
                task_subset.append(task)
    else:
        task_subset = project["tasks"]
    
    # Return initial response to client
    return generate_response(
        data={
            "farming_id": request.project_id,
            "status": "started",
            "tasks": [{"task_name": task["name"], "status": "pending"} for task in task_subset]
        },
        message="Farming started successfully"
    )

@router.get("/logs/{project_id}", response_model=dict)
async def get_farming_logs(
    project_id: str = Path(..., description="Farming project ID"),
    current_user: User = Depends(get_current_user)
):
    """
    Get logs for a specific farming project
    """
    # Check if project exists and belongs to user
    projects_collection = get_collection("farming_projects")
    project = await projects_collection.find_one({"id": project_id, "user_id": current_user.id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found or you don't have access"
        )
    
    # Get logs
    logs_collection = get_collection("farming_logs")
    logs_cursor = logs_collection.find(
        {"project_id": project_id}
    ).sort("created_at", 1)
    
    logs = []
    async for log in logs_cursor:
        logs.append({
            "message": log["message"],
            "level": log["level"],
            "timestamp": log["created_at"].isoformat()
        })
    
    return generate_response(
        data={
            "project_id": project_id,
            "project_name": project["project_name"],
            "status": project["status"],
            "logs": logs
        },
        message="Farming logs retrieved successfully"
    )

@router.get("/my", response_model=dict)
async def get_my_farming_projects(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of user's farming projects
    """
    projects_collection = get_collection("farming_projects")
    
    projects_cursor = projects_collection.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1)
    
    projects = []
    async for project in projects_cursor:
        # Format tasks
        tasks = []
        for task in project["tasks"]:
            tasks.append({
                "name": task["name"],
                "type": task["type"],
                "status": task.get("status", "pending")
            })
        
        # Add to projects list
        projects.append({
            "id": project["id"],
            "name": project["project_name"],
            "chain": project["chain"],
            "tasks": tasks,
            "last_farmed": project["updated_at"].isoformat() if project["status"] != "pending" else None,
            "status": project["status"]
        })
    
    return generate_response(
        data=projects,
        message="Farming projects retrieved successfully"
    )

@router.get("/chains", response_model=dict)
async def get_supported_chains():
    """
    Get list of supported chains
    """
    chains = [
        {"name": "zkSync", "chain_id": 324, "symbol": "ETH", "rpc_url": "https://mainnet.era.zksync.io", "explorer_url": "https://explorer.zksync.io"},
        {"name": "Sui", "chain_id": 784, "symbol": "SUI", "rpc_url": "https://fullnode.mainnet.sui.io", "explorer_url": "https://explorer.sui.io"},
        {"name": "Scroll", "chain_id": 534352, "symbol": "ETH", "rpc_url": "https://scroll.io/rpc", "explorer_url": "https://scrollscan.com"},
        {"name": "opBNB", "chain_id": 204, "symbol": "BNB", "rpc_url": "https://opbnb-mainnet-rpc.bnbchain.org", "explorer_url": "https://opbnb.bscscan.com"},
        {"name": "Berachain", "chain_id": 80085, "symbol": "BERA", "rpc_url": "https://artio.berachain.com", "explorer_url": "https://artio.beratrail.io"}
    ]
    
    return generate_response(
        data=chains,
        message="Supported chains retrieved successfully"
    )

@router.post("/save", response_model=dict)
async def save_farming_project(
    project_id: str = Query(..., description="Project ID"),
    current_user: User = Depends(get_current_user)
):
    """
    Save a project to the user's farming list
    """
    # Check if project exists and belongs to user
    projects_collection = get_collection("farming_projects")
    project = await projects_collection.find_one({"id": project_id, "user_id": current_user.id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found or you don't have access"
        )
    
    # Update project to add it to saved list (recurring flag)
    await projects_collection.update_one(
        {"id": project_id},
        {"$set": {
            "recurring": True,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return generate_response(
        message="Project saved to farming list successfully"
    )
