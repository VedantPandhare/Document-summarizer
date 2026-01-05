from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
import uvicorn
from backend import summarize_text, summarize_text_with_db, get_user_summary_history, get_user_statistics, search_user_summaries, delete_user_summary, get_recent_summaries
from database import db

# Initialize FastAPI app
app = FastAPI(
    title="Document Summarizer API",
    description="AI-powered document summarization using Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic models for request/response
class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to summarize")
    style: Literal["bullet", "abstract", "detailed"] = Field(
        default="bullet", 
        description="Summary style: bullet, abstract, or detailed"
    )

class SummarizeWithDbRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to summarize")
    style: Literal["bullet", "abstract", "detailed"] = Field(
        default="bullet", 
        description="Summary style: bullet, abstract, or detailed"
    )
    user_id: str = Field(..., description="User identifier")
    document_name: str = Field(..., description="Name of the document")
    document_type: str = Field(default="text", description="Type of document")
    file_size: Optional[int] = Field(None, description="File size in bytes")

class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="Generated summary")
    style: str = Field(..., description="Style used for summarization")
    success: bool = Field(..., description="Whether summarization was successful")

class SummarizeWithDbResponse(BaseModel):
    success: bool = Field(..., description="Whether summarization was successful")
    summary: Optional[str] = Field(None, description="Generated summary")
    summary_id: Optional[int] = Field(None, description="Database ID of saved summary")
    quality_metrics: Optional[dict] = Field(None, description="Quality assessment metrics")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    word_count: Optional[int] = Field(None, description="Original text word count")
    summary_word_count: Optional[int] = Field(None, description="Summary word count")
    message: Optional[str] = Field(None, description="Success message")
    warning: Optional[str] = Field(None, description="Warning message if any")
    error: Optional[str] = Field(None, description="Error message if any")

class SummaryHistoryItem(BaseModel):
    id: int = Field(..., description="Summary ID")
    document_name: str = Field(..., description="Document name")
    document_type: str = Field(..., description="Document type")
    summary: str = Field(..., description="Generated summary")
    summary_style: str = Field(..., description="Summary style used")
    quality_score: Optional[float] = Field(None, description="Quality score")
    created_at: str = Field(..., description="Creation timestamp")
    word_count: Optional[int] = Field(None, description="Original word count")
    summary_word_count: Optional[int] = Field(None, description="Summary word count")

class UserStatistics(BaseModel):
    total_summaries: int = Field(..., description="Total number of summaries")
    total_documents: int = Field(..., description="Total documents processed")
    average_quality: float = Field(..., description="Average quality score")
    favorite_style: str = Field(..., description="Most used summary style")
    total_words_processed: int = Field(..., description="Total words processed")

class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status")
    message: str = Field(..., description="Health check message")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information."""
    return HealthResponse(
        status="healthy",
        message="Document Summarizer API is running. Use /docs for interactive documentation."
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="API is operational and ready to process requests"
    )

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_document(request: SummarizeRequest):
    """
    Summarize text using AI with specified style.
    
    - **text**: The text content to summarize
    - **style**: Summary format (bullet, abstract, or detailed)
    
    Returns the generated summary with metadata.
    """
    try:
        # Validate input text
        if not request.text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Text cannot be empty"
            )
        
        # Generate summary using backend
        summary = summarize_text(request.text, request.style)
        
        # Check if summarization was successful
        if summary.startswith("Error"):
            raise HTTPException(
                status_code=500,
                detail=f"Summarization failed: {summary}"
            )
        
        return SummarizeResponse(
            summary=summary,
            style=request.style,
            success=True
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/summarize-with-db", response_model=SummarizeWithDbResponse)
async def summarize_document_with_db(request: SummarizeWithDbRequest):
    """
    Summarize text and save to database with metadata.
    
    - **text**: The text content to summarize
    - **style**: Summary format (bullet, abstract, or detailed)
    - **user_id**: User identifier for database storage
    - **document_name**: Name of the document
    - **document_type**: Type of document
    - **file_size**: File size in bytes (optional)
    
    Returns the generated summary with database metadata.
    """
    try:
        # Validate input text
        if not request.text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Text cannot be empty"
            )
        
        # Generate summary and save to database
        result = summarize_text_with_db(
            text=request.text,
            style=request.style,
            user_id=request.user_id,
            document_name=request.document_name,
            document_type=request.document_type,
            file_size=request.file_size
        )
        
        return SummarizeWithDbResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/user/{user_id}/summaries", response_model=List[SummaryHistoryItem])
async def get_user_summaries(
    user_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of summaries to return"),
    offset: int = Query(0, ge=0, description="Number of summaries to skip")
):
    """
    Get user's summary history with pagination.
    
    - **user_id**: User identifier
    - **limit**: Maximum number of summaries to return (1-100)
    - **offset**: Number of summaries to skip for pagination
    """
    try:
        summaries = get_user_summary_history(user_id, limit, offset)
        return summaries
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving summaries: {str(e)}"
        )

@app.get("/user/{user_id}/statistics", response_model=UserStatistics)
async def get_user_summary_statistics(user_id: str):
    """
    Get user's summary statistics.
    
    - **user_id**: User identifier
    """
    try:
        stats = get_user_statistics(user_id)
        return UserStatistics(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )

@app.get("/user/{user_id}/search")
async def search_user_summaries(
    user_id: str,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    Search through user's summaries.
    
    - **user_id**: User identifier
    - **query**: Search query string
    - **limit**: Maximum number of results to return
    """
    try:
        results = search_user_summaries(user_id, query, limit)
        return {"results": results, "query": query, "count": len(results)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching summaries: {str(e)}"
        )

@app.get("/user/{user_id}/recent")
async def get_recent_user_summaries(
    user_id: str,
    days: int = Query(7, ge=1, le=365, description="Number of days to look back")
):
    """
    Get user's recent summaries from the last N days.
    
    - **user_id**: User identifier
    - **days**: Number of days to look back (1-365)
    """
    try:
        summaries = get_recent_summaries(user_id, days)
        return {"summaries": summaries, "days": days, "count": len(summaries)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving recent summaries: {str(e)}"
        )

@app.delete("/user/{user_id}/summary/{summary_id}")
async def delete_user_summary_endpoint(user_id: str, summary_id: int):
    """
    Delete a user's summary.
    
    - **user_id**: User identifier
    - **summary_id**: ID of the summary to delete
    """
    try:
        success = delete_user_summary(summary_id, user_id)
        if success:
            return {"message": "Summary deleted successfully", "summary_id": summary_id}
        else:
            raise HTTPException(
                status_code=404,
                detail="Summary not found or access denied"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting summary: {str(e)}"
        )

@app.get("/styles")
async def get_available_styles():
    """Get available summary styles."""
    return {
        "styles": [
            {
                "id": "bullet",
                "name": "Bullet Points",
                "description": "Key points in bullet format"
            },
            {
                "id": "abstract", 
                "name": "Abstract",
                "description": "3-4 line concise summary"
            },
            {
                "id": "detailed",
                "name": "Detailed",
                "description": "Comprehensive narrative summary"
            }
        ]
    }

@app.get("/models")
async def get_available_models():
    """Get available Gemini models."""
    try:
        from backend import get_available_models
        models = get_available_models()
        return {"models": models}
    except Exception as e:
        return {"models": [], "error": str(e)}

if __name__ == "__main__":
    # Run with uvicorn when script is executed directly
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
