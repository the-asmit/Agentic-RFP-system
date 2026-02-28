"""Sales proposal agent."""
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.rfp import RFP
from app.schemas.match import MatchResult
from app.schemas.pricing import PricingResult
from app.core.llm import get_llm
from app.core.logging import logger


SALES_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a proposal writer creating an honest RFP response.

Your job is to:
1. Summarize the solution
2. Acknowledge strengths and limitations honestly
3. Make appropriate recommendation based on suitability

⚠️ CRITICAL RULES - NO EXCEPTIONS ⚠️

1. You MUST ONLY reference requirements that are explicitly mentioned in the technical analysis

2. DO NOT add, infer, assume, or generate ANY additional requirements or features

3. DO NOT paraphrase or rephrase requirements - use the EXACT wording from the data

4. DO NOT mention capabilities not explicitly in the provided data

5. DO NOT invent company names, statistics, ROI claims, or testimonials

6. DO NOT create urgency or false claims

7. If something is not in the provided data, DO NOT mention it

Be honest about suitability:
- If "suitable" → recommend confidently
- If "partial" → recommend with clear caveats
- If "not suitable" → be honest about gaps

REMEMBER: Only use information explicitly provided in the input data."""),
    ("user", """Create an honest proposal for this RFP.

RFP:
Title: {rfp_title}
Description: {rfp_description}
Budget: ${budget:,.2f}

Proposed Solution:
Product: {product_name}
Match Score: {match_score}%
Total Price: ${total_price:,.2f}

Suitability: {suitability}
Reason: {suitability_reason}

Technical Analysis:
{technical_analysis}

Pricing Breakdown:
{pricing_explanation}

Create a concise, honest proposal. You MUST ONLY reference information from the data above. Do not add or infer anything. Use exact wording from the technical analysis.""")
])


async def generate_sales_pitch(
    rfp: RFP,
    matches: List[MatchResult],
    pricing: List[PricingResult],
    technical_analysis: str,
    suitability: str = "unknown",
    suitability_reason: str = ""
) -> str:
    """
    Generate honest sales proposal for the best product.
    
    Args:
        rfp: The RFP document
        matches: List containing the single best matched product
        pricing: List containing pricing for the best product
        technical_analysis: Technical analysis from technical agent
        suitability: Suitability classification
        suitability_reason: Reason for suitability
        
    Returns:
        Sales pitch text
    """
    logger.info("Sales agent: Starting pitch generation")
    
    if not matches or not pricing:
        return "Unable to generate proposal due to insufficient data."
    
    # Work with single best product
    best_match = matches[0]
    best_pricing = pricing[0]
    
    try:
        llm = get_llm(temperature=0.1)  # Very low temperature for grounded output
        
        # Format pricing breakdown for prompt
        pricing_breakdown = (f"Base: ${best_pricing.base_price:,.2f}, "
                           f"Tests: ${best_pricing.total_test_cost:,.2f}, "
                           f"Markup: ${best_pricing.markup_amount:,.2f}")
        
        # Generate pitch
        chain = SALES_PROMPT | llm
        response = await chain.ainvoke({
            "rfp_title": rfp.title,
            "rfp_description": rfp.description,
            "budget": rfp.budget or 0,
            "product_name": best_match.product_name,
            "match_score": int(best_match.match_score * 100),
            "total_price": best_pricing.total_price,
            "suitability": suitability,
            "suitability_reason": suitability_reason,
            "technical_analysis": technical_analysis[:500],
            "pricing_explanation": pricing_breakdown
        })
        
        pitch = response.content
        logger.info(f"Sales agent: Pitch generated ({len(pitch)} chars)")
        
        return pitch
    
    except Exception as e:
        logger.error(f"Sales agent: Error generating pitch - {str(e)}")
        # Return fallback pitch
        return (f"Proposal for {rfp.title}\n\n"
                f"Proposed Solution: {best_match.product_name}\n"
                f"Match Score: {best_match.match_score*100:.0f}%\n"
                f"Suitability: {suitability}\n"
                f"Total Price: ${best_pricing.total_price:,.2f}\n\n"
                f"Technical Analysis:\n{technical_analysis[:300]}")
