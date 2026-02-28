"""RFP processing pipeline."""
from app.schemas.proposal import Proposal
from app.services.loader import load_rfp, load_products
from app.core.graph import create_rfp_graph
from app.core.state import RFPState
from app.core.logging import logger


async def run_pipeline(rfp_id: str) -> Proposal:
    """
    Execute the complete RFP processing pipeline.
    
    This is the main entry point for RFP processing. It:
    1. Loads the RFP and products
    2. Creates and executes the LangGraph workflow
    3. Returns the generated proposal
    
    Args:
        rfp_id: RFP identifier (e.g., 'rfp1')
        
    Returns:
        Generated Proposal object
        
    Raises:
        Exception: If processing fails
    """
    logger.info(f"Pipeline: Starting RFP processing for {rfp_id}")
    
    try:
        # Load data
        logger.info(f"Pipeline: Loading RFP {rfp_id}")
        rfp = await load_rfp(rfp_id)
        
        logger.info("Pipeline: Loading products")
        products = await load_products()
        
        # Create initial state
        initial_state: RFPState = {
            "rfp_id": rfp_id,
            "rfp": rfp,
            "products": products
        }
        
        # Create and run graph
        logger.info("Pipeline: Creating workflow graph")
        graph = create_rfp_graph()
        
        logger.info("Pipeline: Executing workflow")
        final_state = await graph.ainvoke(initial_state)
        
        # Extract proposal
        proposal = final_state.get("proposal")
        
        if not proposal:
            logger.error("Pipeline: No proposal generated")
            raise ValueError("Failed to generate proposal")
        
        logger.info(f"Pipeline: Successfully generated proposal for {rfp_id}")
        return proposal
        
    except Exception as e:
        logger.error(f"Pipeline: Error processing RFP {rfp_id}: {str(e)}")
        raise
