
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import List, Optional

from utils.helper import generate_response

router = APIRouter(prefix="/airdrop")

@router.get("/top", response_model=dict)
async def get_top_airdrops():
    """
    Get top trending airdrop projects
    """
    # Mock response, implement actual logic later
    return generate_response(
        data=[
            {
                "id": "mock-airdrop-1",
                "name": "ZKSync Airdrop",
                "description": "Participate in ZKSync ecosystem to qualify",
                "status": "Active",
                "end_date": "2023-12-31",
                "estimated_value": "$500-$2000"
            },
            {
                "id": "mock-airdrop-2",
                "name": "Scroll Airdrop",
                "description": "Participate in Scroll testnet",
                "status": "Active",
                "end_date": "2023-12-15",
                "estimated_value": "$200-$1000"
            }
        ],
        message="Top airdrops retrieved successfully"
    )

@router.get("/latest", response_model=dict)
async def get_latest_airdrops():
    """
    Get latest announced airdrop projects
    """
    # Mock response, implement actual logic later
    return generate_response(
        data=[
            {
                "id": "mock-airdrop-3",
                "name": "Berachain Airdrop",
                "description": "New Layer 1 EVM chain",
                "status": "Announced",
                "start_date": "2023-11-15",
                "requirements": ["Testnet participation", "Discord activity"]
            }
        ],
        message="Latest airdrops retrieved successfully"
    )

@router.post("/save", response_model=dict)
async def save_airdrop_project(airdrop_id: str = Query(..., description="Airdrop project ID")):
    """
    Save an airdrop project to user's list
    """
    # Mock response, implement actual logic later
    return generate_response(
        message="Airdrop project saved successfully"
    )

@router.get("/mine", response_model=dict)
async def get_saved_airdrops():
    """
    Get user's saved airdrop projects
    """
    # Mock response, implement actual logic later
    return generate_response(
        data=[
            {
                "id": "mock-airdrop-1",
                "name": "ZKSync Airdrop",
                "status": "In Progress",
                "tasks_completed": 3,
                "tasks_total": 5
            }
        ],
        message="Saved airdrops retrieved successfully"
    )
