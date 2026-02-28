"""Orchestrator for coordinating multiple agents."""
import asyncio
from typing import List, Dict, Any
from app.schemas.rfp import RFP
from app.schemas.match import MatchResult
from app.schemas.pricing import PricingResult
from app.agents.technical_agent import analyze_technical_fit
from app.agents.pricing_agent import explain_pricing
from app.agents.sales_agent import generate_sales_pitch
from app.core.logging import logger


async def run_agents(
    rfp: RFP,
    matches: List[MatchResult],
    pricing: List[PricingResult],
    suitability: str = "unknown",
    suitability_reason: str = ""
) -> Dict[str, Any]:
    """
    Orchestrate all agents to generate complete proposal content.
    
    Args:
        rfp: RFP document
        matches: Matched products
        pricing: Pricing results
        suitability: Suitability classification (suitable/partial/not suitable)
        suitability_reason: Reason for suitability classification
        
    Returns:
        Dictionary with agent outputs
    """
    logger.info("Orchestrator: Running all agents")
    
    # Run technical and pricing agents concurrently (independent)
    logger.info("Orchestrator: Calling technical and pricing agents")
    
    try:
        technical_task = analyze_technical_fit(rfp, matches, suitability, suitability_reason)
        pricing_task = explain_pricing(pricing)
        
        results = await asyncio.gather(
            technical_task,
            pricing_task,
            return_exceptions=True
        )
        
        technical_analysis = results[0]
        pricing_explanation = results[1]
        
        # Handle technical agent errors
        if isinstance(technical_analysis, Exception):
            logger.error(f"Orchestrator: Technical agent failed - {str(technical_analysis)}")
            technical_analysis = "Technical analysis unavailable due to an error."
        
        # Handle pricing agent errors
        if isinstance(pricing_explanation, Exception):
            logger.error(f"Orchestrator: Pricing agent failed - {str(pricing_explanation)}")
            pricing_explanation = "Pricing explanation unavailable due to an error."
        
        # Run sales agent (depends on technical analysis)
        logger.info("Orchestrator: Calling sales agent")
        try:
            sales_pitch = await generate_sales_pitch(
                rfp, matches, pricing, technical_analysis, suitability, suitability_reason
            )
        except Exception as e:
            logger.error(f"Orchestrator: Sales agent failed - {str(e)}")
            sales_pitch = "Sales proposal unavailable due to an error."
        
        logger.info("Orchestrator: All agents completed")
        
        return {
            "technical_analysis": technical_analysis,
            "pricing_explanation": pricing_explanation,
            "sales_pitch": sales_pitch
        }
        
    except Exception as e:
        logger.error(f"Orchestrator: Critical error in agent orchestration - {str(e)}")
        # Return default values if everything fails
        return {
            "technical_analysis": "Technical analysis unavailable.",
            "pricing_explanation": "Pricing explanation unavailable.",
            "sales_pitch": "Sales proposal unavailable."
        }
