"""RFP schema definitions."""
from typing import List, Optional
from pydantic import BaseModel, Field


class RFP(BaseModel):
    """Request for Proposal model."""
    
    id: str = Field(..., description="Unique RFP identifier")
    title: str = Field(..., description="RFP title")
    description: str = Field(..., description="Detailed RFP description")
    requirements: List[str] = Field(..., description="List of requirements")
    deadline: str = Field(..., description="Submission deadline")
    budget: Optional[float] = Field(None, description="Budget constraint")
    evaluation_criteria: Optional[List[str]] = Field(None, description="Evaluation criteria")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "rfp-2024-001",
                "title": "Enterprise Security Solution",
                "description": "Comprehensive security solution needed",
                "requirements": ["firewall", "VPN", "intrusion detection"],
                "deadline": "2026-04-15",
                "budget": 50000
            }
        }
