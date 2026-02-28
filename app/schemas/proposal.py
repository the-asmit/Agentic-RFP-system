"""Proposal schema definitions."""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.match import MatchResult
from app.schemas.pricing import PricingResult


class Proposal(BaseModel):
    """Final proposal model."""
    
    rfp_id: str = Field(..., description="RFP identifier")
    rfp_title: str = Field(..., description="RFP title")
    matches: List[MatchResult] = Field(..., description="Matched products")
    selection_justification: Optional[str] = Field(None, description="Why this product was selected")
    suitability: Optional[str] = Field(None, description="suitable | partial | not suitable")
    suitability_reason: Optional[str] = Field(None, description="Why this suitability rating")
    rejected_products: Optional[List[dict]] = Field(None, description="Other products and why they were rejected")
    pricing: List[PricingResult] = Field(..., description="Pricing details")
    technical_analysis: str = Field(..., description="Technical agent analysis")
    pricing_explanation: str = Field(..., description="Pricing agent explanation")
    sales_pitch: str = Field(..., description="Sales agent pitch")
    total_value: float = Field(..., description="Total proposal value")
    generated_at: str = Field(..., description="Generation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rfp_id": "rfp-2024-001",
                "rfp_title": "Enterprise Security Solution",
                "matches": [],
                "pricing": [],
                "technical_analysis": "Technical analysis here",
                "pricing_explanation": "Pricing explanation here",
                "sales_pitch": "Sales pitch here",
                "total_value": 23750,
                "generated_at": "2026-02-28T10:00:00Z"
            }
        }
