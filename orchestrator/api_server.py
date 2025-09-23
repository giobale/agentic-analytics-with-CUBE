# ABOUTME: FastAPI server for orchestrator REST API endpoints
# ABOUTME: Handles frontend requests for natural language query processing

import os
import json
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from orchestrator import QueryOrchestrator

# Request/Response models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    description: str
    response_type: str
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    csv_filename: Optional[str] = None
    row_count: Optional[int] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str

class ReadinessResponse(BaseModel):
    status: str
    system_prompt_cached: bool

# Initialize FastAPI app
app = FastAPI(
    title="CUBE Query Orchestrator API",
    description="Natural language to CUBE query processing service",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator
    try:
        # Get configuration from environment variables
        cube_base_url = os.getenv('CUBE_BASE_URL', 'http://localhost:4000')
        cube_api_secret = os.getenv('CUBEJS_API_SECRET', 'baubeach')
        openai_api_key = os.getenv('OPENAI_API_KEY')

        orchestrator = QueryOrchestrator(
            openai_api_key=openai_api_key,
            cube_base_url=cube_base_url,
            cube_api_secret=cube_api_secret
        )
        init_result = orchestrator.initialize()

        if not init_result["success"]:
            print(f"Warning: Orchestrator initialization had issues: {init_result['errors']}")
        else:
            print("✅ Orchestrator initialized successfully")

    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {str(e)}")
        orchestrator = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="orchestrator",
        timestamp=datetime.now().isoformat()
    )

@app.get("/readyz", response_model=ReadinessResponse)
async def readiness_check():
    """Readiness check endpoint"""
    system_prompt_cached = False

    if orchestrator:
        cache_file = orchestrator.system_prompt_cache_file
        system_prompt_cached = os.path.exists(cache_file)

    return ReadinessResponse(
        status="ready" if system_prompt_cached else "not_ready",
        system_prompt_cached=system_prompt_cached
    )

@app.get("/system-prompt-info")
async def system_prompt_info():
    """Get system prompt metadata"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        metadata_file = orchestrator.system_prompt_metadata_file
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                return json.load(f)
        else:
            raise HTTPException(status_code=404, detail="System prompt metadata not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading metadata: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        print(f"🔍 API DEBUG: Received query request: {request.query}")
        # Process the query
        print("🔍 API DEBUG: Calling orchestrator.process_query...")
        result = orchestrator.process_query(request.query)
        print(f"🔍 API DEBUG: Orchestrator result success: {result.get('success', False)}")
        print(f"🔍 API DEBUG: Orchestrator result type: {result.get('response_type', 'unknown')}")

        if result["success"]:
            print("🔍 API DEBUG: Result is successful, processing response...")
            if result["response_type"] == "data_result":
                print("🔍 API DEBUG: Creating data_result response...")
                print(f"   Description: {result['llm_response'].get('description', 'Query processed successfully')}")
                print(f"   CSV filename: {result.get('csv_filename')}")
                print(f"   Row count: {result.get('row_count')}")
                cube_data = result.get('cube_data')
                if cube_data:
                    if isinstance(cube_data, list):
                        print(f"   Data: List with {len(cube_data)} items")
                        if cube_data and isinstance(cube_data[0], dict):
                            print(f"   First item keys: {list(cube_data[0].keys())}")
                    elif isinstance(cube_data, dict):
                        print(f"   Data keys: {list(cube_data.keys())}")
                    else:
                        print(f"   Data type: {type(cube_data)}")
                else:
                    print("   Data: None")

                response = QueryResponse(
                    success=True,
                    description=result["llm_response"].get("description", "Query processed successfully"),
                    response_type="data_result",
                    data=result.get("cube_data"),
                    csv_filename=result.get("csv_filename"),
                    row_count=result.get("row_count")
                )
                print("✅ API DEBUG: QueryResponse created successfully")
                return response
            elif result["response_type"] == "clarification":
                return QueryResponse(
                    success=True,
                    description="I need more information to process your query",
                    response_type="clarification",
                    data={
                        "clarification_questions": result["llm_response"].get("clarification_questions", []),
                        "suggestions": result["llm_response"].get("suggestions", [])
                    }
                )
            else:
                return QueryResponse(
                    success=False,
                    description="Unknown response type",
                    response_type="error",
                    error=f"Unexpected response type: {result['response_type']}"
                )
        else:
            return QueryResponse(
                success=False,
                description="Failed to process query",
                response_type="error",
                error=result.get("error", "Unknown error occurred")
            )

    except Exception as e:
        print(f"❌ API DEBUG: Exception in process_query: {str(e)}")
        print(f"❌ API DEBUG: Exception type: {type(e).__name__}")
        import traceback
        print(f"❌ API DEBUG: Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated CSV files"""
    # Security: Only allow downloading from results directory
    if not filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files can be downloaded")

    # Check for path traversal attacks
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Look for file in common result directories
    possible_paths = [
        f"/app/results/{filename}",
        f"/app/orchestrator/tests/results/{filename}",
        f"/tmp/{filename}"
    ]

    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='text/csv'
    )

@app.get("/conversation")
async def get_conversation():
    """Get conversation history"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        return orchestrator.get_conversation_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")

@app.delete("/conversation")
async def clear_conversation():
    """Clear conversation history"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        orchestrator.clear_conversation()
        return {"message": "Conversation cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing conversation: {str(e)}")

@app.get("/status")
async def get_status():
    """Get orchestrator status"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        return orchestrator.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)