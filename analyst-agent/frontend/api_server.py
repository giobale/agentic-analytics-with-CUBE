# ABOUTME: FastAPI server for analyst agent API endpoints
# ABOUTME: Handles requests from chat frontend to initiate analysis with CSV and query

import os
import sys
import tempfile
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
import uvicorn

# Add analyst-service to path
current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_file_dir)
analyst_service_root = os.path.join(project_root, 'analyst-service')
analyst_service_src = os.path.join(analyst_service_root, 'src')

if analyst_service_root not in sys.path:
    sys.path.insert(0, analyst_service_root)
if analyst_service_src not in sys.path:
    sys.path.insert(0, analyst_service_src)

# Request/Response models
class AnalysisRequest(BaseModel):
    csv_content: str
    query: str
    filename: Optional[str] = None

class CSVUploadRequest(BaseModel):
    csv_content: str
    filename: Optional[str] = None

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    streamlit_url: Optional[str] = None
    analysis_id: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str

# Initialize FastAPI app
app = FastAPI(
    title="Analyst Agent API",
    description="API interface for starting analysis from chat frontend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_csv_to_datasets(csv_content: str, filename: Optional[str] = None) -> str:
    """Save CSV content to analyst-service/datasets directory."""
    try:
        # Create filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"chat_analysis_{timestamp}.csv"
        elif not filename.endswith('.csv'):
            filename += '.csv'

        # Ensure datasets directory exists
        datasets_dir = os.path.join(analyst_service_root, 'datasets')
        os.makedirs(datasets_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(datasets_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        logger.info(f"CSV saved to {file_path}")
        return filename

    except Exception as e:
        logger.error(f"Error saving CSV: {str(e)}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="analyst-agent-api",
        timestamp=datetime.now().isoformat()
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest):
    """Start analysis with CSV content and query."""
    try:
        logger.info(f"Received analysis request with query: {request.query}")

        # Save CSV to datasets directory
        filename = save_csv_to_datasets(request.csv_content, request.filename)

        # Generate analysis ID for tracking
        analysis_id = str(uuid.uuid4())[:8]

        # Construct Streamlit URL with parameters
        streamlit_port = os.getenv('STREAMLIT_PORT', '8501')
        base_url = f"http://localhost:{streamlit_port}"

        # URL encode parameters
        import urllib.parse
        query_param = urllib.parse.quote(request.query)
        filename_param = urllib.parse.quote(filename)

        streamlit_url = f"{base_url}/?dataset={filename_param}&query={query_param}&analysis_id={analysis_id}"

        logger.info(f"Analysis initiated with ID: {analysis_id}")
        logger.info(f"Streamlit URL: {streamlit_url}")

        return AnalysisResponse(
            success=True,
            message="Analysis initiated successfully",
            streamlit_url=streamlit_url,
            analysis_id=analysis_id
        )

    except Exception as e:
        logger.error(f"Error starting analysis: {str(e)}")
        return AnalysisResponse(
            success=False,
            message="Failed to start analysis",
            error=str(e)
        )

@app.post("/upload-csv", response_model=AnalysisResponse)
async def upload_csv(request: CSVUploadRequest):
    """Upload CSV content only, without query."""
    try:
        logger.info("Received CSV upload request from chat frontend")

        # Save CSV to datasets directory
        filename = save_csv_to_datasets(request.csv_content, request.filename)

        # Construct Streamlit URL without query parameter
        streamlit_port = os.getenv('STREAMLIT_PORT', '8501')
        base_url = f"http://localhost:{streamlit_port}"

        # URL encode filename parameter
        import urllib.parse
        filename_param = urllib.parse.quote(filename)

        streamlit_url = f"{base_url}/?dataset={filename_param}"

        logger.info(f"CSV uploaded successfully: {filename}")
        logger.info(f"Streamlit URL: {streamlit_url}")

        return AnalysisResponse(
            success=True,
            message="CSV uploaded successfully",
            streamlit_url=streamlit_url
        )

    except Exception as e:
        logger.error(f"Error uploading CSV: {str(e)}")
        return AnalysisResponse(
            success=False,
            message="Failed to upload CSV",
            error=str(e)
        )

@app.post("/upload-and-analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    query: str = Form(...)
):
    """Upload CSV file and start analysis."""
    try:
        logger.info(f"Received file upload: {file.filename} with query: {query}")

        # Read file content
        csv_content = await file.read()
        csv_content = csv_content.decode('utf-8')

        # Use the uploaded filename
        filename = file.filename if file.filename else "uploaded_data.csv"

        # Create analysis request
        request = AnalysisRequest(
            csv_content=csv_content,
            query=query,
            filename=filename
        )

        # Process the request
        return await start_analysis(request)

    except Exception as e:
        logger.error(f"Error in upload and analyze: {str(e)}")
        return AnalysisResponse(
            success=False,
            message="Failed to upload and analyze",
            error=str(e)
        )

if __name__ == "__main__":
    port = int(os.getenv('ANALYST_API_PORT', '8502'))
    uvicorn.run(app, host="0.0.0.0", port=port)