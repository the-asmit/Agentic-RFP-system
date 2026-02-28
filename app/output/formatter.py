"""Proposal formatter."""
from datetime import datetime
from app.schemas.proposal import Proposal
from app.core.state import RFPState
from app.core.logging import logger


async def format_proposal(state: RFPState) -> Proposal:
    """
    Format the final proposal from state.
    
    Args:
        state: Complete RFP processing state
        
    Returns:
        Formatted Proposal object
        
    Raises:
        ValueError: If required state fields are missing
    """
    logger.info(f"Formatter: Creating proposal for RFP {state.get('rfp_id', 'unknown')}")
    
    # Validate required fields
    rfp = state.get("rfp")
    matches = state.get("matches", [])
    pricing = state.get("pricing", [])
    
    if not rfp:
        logger.error("Formatter: Missing RFP in state")
        raise ValueError("Cannot format proposal: RFP data is missing")
    
    if not matches:
        logger.warning("Formatter: No matches found in state")
    
    if not pricing:
        logger.warning("Formatter: No pricing found in state")
    
    # Get selection decision info
    selection_justification = state.get("selection_justification", None)
    rejected_products = state.get("rejected_products", [])
    suitability = state.get("suitability", None)
    suitability_reason = state.get("suitability_reason", None)
    
    # Get agent outputs with defaults
    technical_analysis = state.get("technical_analysis", "No technical analysis available.")
    pricing_explanation = state.get("pricing_explanation", "No pricing explanation available.")
    sales_pitch = state.get("sales_pitch", "No sales pitch available.")
    
    # Calculate total value
    total_value = sum(p.total_price for p in pricing) if pricing else 0
    
    # Create proposal
    proposal = Proposal(
        rfp_id=rfp.id,
        rfp_title=rfp.title,
        matches=matches,
        selection_justification=selection_justification,
        suitability=suitability,
        suitability_reason=suitability_reason,
        rejected_products=rejected_products if rejected_products else None,
        pricing=pricing,
        technical_analysis=technical_analysis,
        pricing_explanation=pricing_explanation,
        sales_pitch=sales_pitch,
        total_value=total_value,
        generated_at=datetime.utcnow().isoformat() + "Z"
    )
    
    logger.info(f"Formatter: Proposal created with {len(matches)} products, total ${total_value:,.2f}")
    
    return proposal
