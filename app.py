# main.py - FastAPI Multi-Repo Ideation Backend

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import asyncio
import logging
from contextlib import asynccontextmanager

# Import the existing modules (assuming they're in your project)
from extractor.clone_repo import clone_repo
from extractor.parse_repo import parse_repo
from extractor.summarizer import extract_features_and_techstack, suggest_new_features_from_features, suggest_new_tech_stack_from_tech_stack # <--- UPDATED IMPORT
from database.db import init_db, insert_project, insert_features, insert_tech_stack, insert_ideated_features, insert_ideated_tech_stack # <--- UPDATED IMPORT for DB
from utils.helpers import parse_llm_summary
from github_search import search_similar_repositories

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_db()
    logger.info("Database initialized")
    yield
    # Cleanup on shutdown if needed
    logger.info("Application shutting down")

# FastAPI app
app = FastAPI(
    title="Multi-Repo Feature Ideation API",
    description="Generate feature ideas for your project by analyzing similar GitHub repositories",
    version="1.0.0",
    lifespan=lifespan
)

# Pydantic models
class IdeationRequest(BaseModel):
    project_idea: str = Field(..., description="Description of your project idea", min_length=3, max_length=500)
    max_repos: int = Field(default=3, ge=1, le=10, description="Number of repositories to analyze (1-10)")

class RepositoryInfo(BaseModel):
    name: str
    url: str
    features: List[str]
    tech_stack: List[str]

class IdeationResponse(BaseModel):
    project_idea: str
    analyzed_repos: List[RepositoryInfo]
    aggregated_features: List[str]
    aggregated_tech_stack: List[str]
    suggested_features: str
    suggested_tech_stack: str # <--- NEW FIELD
    total_repos_processed: int

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# Helper function to process a single repository
async def process_repository(repo_info: dict) -> Optional[RepositoryInfo]:
    """Process a single repository and extract features/tech stack"""
    try:
        logger.info(f"Processing repository: {repo_info['name']}")
        
        # Clone repository
        local_path = clone_repo(repo_info["url"])
        if not local_path:
            logger.warning(f"Failed to clone repository: {repo_info['name']}")
            return None
        
        # Parse repository
        repo_data = parse_repo(local_path)
        
        # Extract features and tech stack using LLM
        summary = extract_features_and_techstack(repo_data)
        features, tech_stack = parse_llm_summary(summary)
        
        return RepositoryInfo(
            name=repo_info["name"],
            url=repo_info["url"],
            features=features,
            tech_stack=tech_stack
        )
        
    except Exception as e:
        logger.error(f"Error processing repository {repo_info['name']}: {str(e)}")
        return None

# API Endpoints
@app.get("/", summary="Health Check")
async def root():
    """Health check endpoint"""
    return {"message": "Multi-Repo Feature Ideation API is running!", "status": "healthy"}

@app.post("/ideate", response_model=IdeationResponse, summary="Generate Feature Ideas")
async def generate_feature_ideas(request: IdeationRequest):
    """
    Generate feature ideas for a project by analyzing similar GitHub repositories.
    
    This endpoint:
    1. Searches GitHub for repositories similar to your project idea
    2. Clones and analyzes the top repositories
    3. Extracts features and tech stack from each repository
    4. Aggregates all features and generates new feature suggestions
    5. Stores the results in the database
    """
    try:
        logger.info(f"Starting ideation for: {request.project_idea}")
        
        # Search for similar repositories
        logger.info("Searching GitHub for similar repositories...")
        repo_candidates = search_similar_repositories(request.project_idea, request.max_repos)
        
        if not repo_candidates:
            raise HTTPException(status_code=404, detail="No repositories found for the given project idea")
        
        logger.info(f"Found {len(repo_candidates)} repositories")
        
        # Process repositories (you might want to make this truly async in production)
        processed_repos = []
        aggregated_features = []
        aggregated_tech_stack = []
        
        for repo_info in repo_candidates:
            processed_repo = await process_repository(repo_info)
            if processed_repo:
                processed_repos.append(processed_repo)
                aggregated_features.extend(processed_repo.features)
                aggregated_tech_stack.extend(processed_repo.tech_stack)
        
        if not processed_repos:
            raise HTTPException(status_code=500, detail="Failed to process any repositories")
        
        # Deduplicate features and tech stack
        unique_features = list(dict.fromkeys(aggregated_features))
        unique_tech_stack = list(dict.fromkeys(aggregated_tech_stack))
        
        if not unique_features:
            raise HTTPException(status_code=404, detail="No features extracted from the analyzed repositories")
        
        # Generate new feature ideas
        logger.info("Generating new feature suggestions...")
        suggested_features = suggest_new_features_from_features("\n".join(unique_features))

        # Generate new tech stack suggestions # <--- NEW CALL
        logger.info("Generating new tech stack suggestions...")
        suggested_tech_stack = suggest_new_tech_stack_from_tech_stack("\n".join(unique_tech_stack))
        
        # Store in database
        logger.info("Storing results in database...")
        project_id = insert_project(f"[MultiRepo:{request.project_idea}]", "virtual")
        insert_features(project_id, unique_features)
        insert_tech_stack(project_id, unique_tech_stack)
        insert_ideated_features(project_id, suggested_features)
        insert_ideated_tech_stack(project_id, suggested_tech_stack) # <--- NEW DB INSERTION
        
        logger.info("Ideation completed successfully")
        
        return IdeationResponse(
            project_idea=request.project_idea,
            analyzed_repos=processed_repos,
            aggregated_features=unique_features,
            aggregated_tech_stack=unique_tech_stack,
            suggested_features=suggested_features,
            suggested_tech_stack=suggested_tech_stack, # <--- NEW FIELD IN RESPONSE
            total_repos_processed=len(processed_repos)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during ideation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/status", summary="API Status")
async def get_status():
    """Get API status and configuration"""
    return {
        "status": "active",
        "github_token_configured": bool(os.getenv("GITHUB_TOKEN")),
        "max_repos_limit": 10,
        "database_initialized": True
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "details": str(exc)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)