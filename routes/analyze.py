from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from models.user import User
from schemas.analyze import (
    ProjectAnalyzeRequest,
    AnalyzeHistoryRequest,
    FetcherRequest,
    ProjectIdRequest
)
from utils.jwt import get_current_user
from services.fetcher_runner import FetcherRunner
from core.database import db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["Analyzer"])


def generate_response(data: dict, message: str, status_code: int = 200):
    return JSONResponse(content={"data": data, "message": message}, status_code=status_code)


@router.post("")
async def analyze_project(
    request: ProjectAnalyzeRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    runner = FetcherRunner(
        project_name=request.project_name,
        website=request.website,
        fetch_type="all"
    )
    result = await runner.analyze_project(
        project_data=request.dict(),
        user=current_user
    )
    return generate_response(data=result, message="Project analysis initiated")


@router.post("/fetcher")
async def run_fetcher_by_type(
    request: FetcherRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    runner = FetcherRunner(
        project_name=request.project_name,
        website=request.website,
        fetch_type=request.fetcher_type
    )
    result = await runner.run_specific_fetcher(
        project_id=request.project_id,
        fetcher_type=request.fetcher_type,
        user=current_user
    )
    return generate_response(data=result, message="Fetcher executed successfully")


@router.post("/history")
async def get_analyze_history(
    request: AnalyzeHistoryRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        logger.error("User not authenticated")
        raise HTTPException(status_code=401, detail="User not authenticated")
    logger.info(f"Fetching analysis history for user_id={current_user.id}, project_name={request.project_name}")
    query = {
        "user_id": current_user.id,
        "project_name": request.project_name
    }
    result = await db["fetchers_results"].find_one(query)
    if not result:
        logger.warning(f"No history found for query: {query}")
        raise HTTPException(status_code=404, detail="No history found")
    logger.info(f"History found: {result}")
    return generate_response(data=result, message="Analysis history retrieved")


@router.post("/delete")
async def delete_analyze_result(
    request: ProjectIdRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    deleted = await db["projects"].delete_one({
        "_id": request.project_id,
        "user_id": current_user.id
    })
    return generate_response(data={"deleted_count": deleted.deleted_count})
