from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

from models.user import User
from core.database import get_collection
from services.fetcher_handler import FetcherHandler
from utils.helper import generate_id

logger = logging.getLogger(__name__)

class FetcherRunner:
    """Manages the execution of multiple fetchers for a project analysis"""
    
    def __init__(self, project_name: str, website: str, fetch_type: str):
        self.fetcher_handler = FetcherHandler(project_name, website, fetch_type)
    
    async def analyze_project(
        self, 
        project_data: Dict[str, Any],
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Run analysis on a project using multiple fetchers"""
        # Generate project ID
        project_id = generate_id("prj_")
        
        # Create project record
        project_record = {
            "id": project_id,
            "name": project_data.get("name"),
            "website": project_data.get("website"),
            "requested_by": user.id if user else None,
            "created_at": datetime.utcnow(),
            "status": "in_progress",
            "fetchers_available": self.fetcher_handler.available_fetchers,
            "fetchers_completed": [],
            "fetchers_results": {},
            "analysis_summary": None
        }
        
        # Save initial project record
        projects_collection = get_collection("projects")
        await projects_collection.insert_one(project_record)
        
        # Register analysis job in background (simulated)
        asyncio.create_task(self._run_analysis_job(project_id, project_data))
        
        return {
            "project_id": project_id,
            "name": project_data.get("name"),
            "status": "in_progress",
            "fetchers_available": self.fetcher_handler.available_fetchers
        }
    
    async def _run_analysis_job(self, project_id: str, project_data: Dict[str, Any]):
        """Background task to run all fetchers"""
        projects_collection = get_collection("projects")
        
        # Run a subset of fetchers initially
        initial_fetchers = ["about", "team", "social"]
        fetchers_results = {}
        
        for fetcher_type in initial_fetchers:
            # Run fetcher
            fetcher_result = await self.fetcher_handler.run_fetcher(fetcher_type, project_data)
            
            # Store result
            fetchers_results[fetcher_type] = fetcher_result
            
            # Update project record
            await projects_collection.update_one(
                {"id": project_id},
                {
                    "$push": {"fetchers_completed": fetcher_type},
                    "$set": {
                        f"fetchers_results.{fetcher_type}": fetcher_result,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Simulate delay between fetchers
            await asyncio.sleep(1)
        
        # Generate a simple analysis summary
        summary = {
            "name": project_data.get("name"),
            "description": fetchers_results.get("about", {}).get("data", {}).get("description", "No description available"),
            "team_score": 7.5,  # Mock score
            "social_score": 8.2,  # Mock score
            "overall_risk": "Medium",
            "recommendation": "This project shows promise but requires further verification.",
            "completed_at": datetime.utcnow().isoformat()
        }
        
        # Update project with summary and mark as completed
        await projects_collection.update_one(
            {"id": project_id},
            {
                "$set": {
                    "status": "completed",
                    "analysis_summary": summary,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    async def run_specific_fetcher(
        self,
        project_id: str,
        fetcher_type: str,
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Run a specific fetcher for an existing project"""
        projects_collection = get_collection("projects")
        
        # Get project
        project = await projects_collection.find_one({"id": project_id})
        if not project:
            return {
                "status": "error",
                "message": f"Project with ID {project_id} not found"
            }
        
        # Check if fetcher is available
        if fetcher_type not in self.fetcher_handler.available_fetchers:
            return {
                "status": "error",
                "message": f"Fetcher '{fetcher_type}' not available"
            }
        
        # Check if fetcher has already been run
        if fetcher_type in project.get("fetchers_completed", []):
            existing_result = project.get("fetchers_results", {}).get(fetcher_type, {})
            return {
                "status": "success",
                "message": f"Fetcher '{fetcher_type}' already run for this project",
                "data": existing_result.get("data"),
                "cached": True
            }
        
        # Run fetcher
        project_data = {
            "name": project.get("name"),
            "website": project.get("website")
        }
        fetcher_result = await self.fetcher_handler.run_fetcher(fetcher_type, project_data)
        
        # Update project record
        await projects_collection.update_one(
            {"id": project_id},
            {
                "$push": {"fetchers_completed": fetcher_type},
                "$set": {
                    f"fetchers_results.{fetcher_type}": fetcher_result,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # If user is provided, charge credits (simulated)
        if user:
            await self._charge_user_credits(user.id, 1, f"Used {fetcher_type} fetcher")
        
        return {
            "status": "success",
            "message": f"Successfully ran {fetcher_type} fetcher",
            "data": fetcher_result.get("data"),
            "cached": False
        }
    
    async def _charge_user_credits(self, user_id: str, amount: int, description: str):
        """Charge user credits for an action"""
        users_collection = get_collection("users")
        
        # Update user credits
        result = await users_collection.update_one(
            {"id": user_id},
            {"$inc": {"credits": -amount}}
        )
        
        if result.modified_count == 1:
            # Log credit usage
            credit_logs_collection = get_collection("credit_logs")
            await credit_logs_collection.insert_one({
                "user_id": user_id,
                "action": "use",
                "amount": -amount,
                "description": description,
                "timestamp": datetime.utcnow()
            })
            
            logger.info(f"Charged {amount} credits from user {user_id} for {description}")
        else:
            logger.error(f"Failed to charge credits from user {user_id}")
