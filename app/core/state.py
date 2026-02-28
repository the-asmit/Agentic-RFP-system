"""State definitions for LangGraph workflow."""
from typing import TypedDict, List, Optional
from app.schemas.rfp import RFP
from app.schemas.product import Product
from app.schemas.match import MatchResult
from app.schemas.pricing import PricingResult
from app.schemas.proposal import Proposal


class RFPState(TypedDict, total=False):
    """
    State for RFP processing workflow.
    
    All fields are optional to allow partial updates from nodes.
    """
    
    # Input
    rfp_id: str
    rfp: Optional[RFP]
    products: Optional[List[Product]]
    
    # Matching results
    matches: Optional[List[MatchResult]]
    all_matches: Optional[List[MatchResult]]  # All matches before selection
    
    # Selection decision
    selection_justification: Optional[str]
    rejected_products: Optional[List[dict]]
    suitability: Optional[str]  # "suitable" | "partial" | "not suitable"
    suitability_reason: Optional[str]
    
    # Pricing results
    pricing: Optional[List[PricingResult]]
    
    # Agent outputs
    technical_analysis: Optional[str]
    pricing_explanation: Optional[str]
    sales_pitch: Optional[str]
    
    # Final output
    proposal: Optional[Proposal]
    
    # Error handling
    error: Optional[str]
