"""API routes for RFP processing."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.schemas.proposal import Proposal
from app.pipelines.rfp_pipeline import run_pipeline
from app.core.logging import logger

router = APIRouter()


class ProcessRFPRequest(BaseModel):
    """Request model for RFP processing."""
    rfp_id: str = Field(..., description="RFP identifier (e.g., 'rfp1')")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        message="Agentic RFP Processing System is running"
    )


@router.post("/process-rfp", response_model=Proposal)
async def process_rfp(request: ProcessRFPRequest):
    """
    Process an RFP and generate a proposal.
    
    This endpoint:
    1. Loads the specified RFP
    2. Matches products to RFP requirements
    3. Calculates pricing
    4. Runs AI agents to generate analysis
    5. Returns a complete proposal
    
    Args:
        request: ProcessRFPRequest with rfp_id
        
    Returns:
        Generated Proposal
        
    Raises:
        HTTPException: If processing fails
    """
    logger.info(f"API: Received request to process RFP {request.rfp_id}")
    
    try:
        # Run the pipeline
        proposal = await run_pipeline(request.rfp_id)
        
        logger.info(f"API: Successfully processed RFP {request.rfp_id}")
        return proposal
        
    except FileNotFoundError as e:
        logger.error(f"API: RFP not found - {str(e)}")
        raise HTTPException(status_code=404, detail=f"RFP not found: {request.rfp_id}")
        
    except ValueError as e:
        logger.error(f"API: Invalid data - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"API: Error processing RFP - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing RFP: {str(e)}")
