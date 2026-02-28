"""Technical analysis agent."""
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.rfp import RFP
from app.schemas.match import MatchResult
from app.core.llm import get_llm
from app.core.logging import logger


TECHNICAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a technical analyst evaluating if a product meets RFP requirements.

Your job is to:
1. List which RFP requirements are matched by the product
2. List which requirements are missing
3. Assess overall suitability

⚠️ CRITICAL RULES - NO EXCEPTIONS ⚠️

1. You MUST ONLY use the EXACT requirements from these two lists:
   - Matched Requirements (matched_specs)
   - Missing Requirements (missing_requirements)

2. DO NOT add, infer, assume, or generate ANY additional requirements

3. DO NOT paraphrase or rephrase the requirements - use the EXACT wording

4. DO NOT generalize requirements (e.g., don't say "authentication" if the list says "multi-factor authentication")

5. DO NOT expand on requirements (e.g., don't add "SAML support" if only "authentication" is listed)

6. If a requirement is NOT in either list, DO NOT mention it at all

7. Use requirements VERBATIM - copy them exactly as provided

REMEMBER: If something is not explicitly in the matched or missing list, it does not exist."""),
    ("user", """Analyze this product match for the RFP.

RFP Details:
Title: {rfp_title}
Description: {rfp_description}
Requirements: {rfp_requirements}

Selected Product:
Name: {product_name}
Match Score: {match_score}

✅ MATCHED REQUIREMENTS (use these EXACT words):
{matched_specs}

❌ MISSING REQUIREMENTS (use these EXACT words):
{missing_requirements}

Suitability Assessment: {suitability}
Reason: {suitability_reason}

Provide a factual technical analysis. You MUST ONLY reference requirements from the two lists above. Use exact wording. Do not add or infer anything.""")
])


async def analyze_technical_fit(rfp: RFP, matches: List[MatchResult], suitability: str = "unknown", suitability_reason: str = "") -> str:
    """
    Generate technical analysis of the best product match.
    
    Args:
        rfp: The RFP document
        matches: List containing the single best matched product
        suitability: Suitability classification
        suitability_reason: Reason for suitability
        
    Returns:
        Technical analysis text
    """
    logger.info("Technical agent: Starting analysis")
    
    if not matches:
        return "No product selected for analysis."
    
    # Work with the single best product
    best_match = matches[0]
    
    try:
        llm = get_llm(temperature=0.1)  # Very low temperature for strict adherence
        
        # Generate analysis
        chain = TECHNICAL_PROMPT | llm
        response = await chain.ainvoke({
            "rfp_title": rfp.title,
            "rfp_description": rfp.description,
            "rfp_requirements": ", ".join(rfp.requirements),
            "product_name": best_match.product_name,
            "match_score": f"{best_match.match_score:.2f}",
            "matched_specs": ", ".join(best_match.matched_specs) if best_match.matched_specs else "None",
            "missing_requirements": ", ".join(best_match.missing_requirements) if best_match.missing_requirements else "None",
            "suitability": suitability,
            "suitability_reason": suitability_reason
        })
        
        analysis = response.content
        logger.info(f"Technical agent: Analysis generated ({len(analysis)} chars)")
        
        return analysis
    
    except Exception as e:
        logger.error(f"Technical agent: Error generating analysis - {str(e)}")
        # Return fallback analysis
        return (f"Technical Analysis for {best_match.product_name}:\n"
                f"Match Score: {best_match.match_score*100:.0f}%\n"
                f"Suitability: {suitability}\n"
                f"Matched Specs: {', '.join(best_match.matched_specs[:5])}\n"
                f"Missing Requirements: {', '.join(best_match.missing_requirements[:3]) if best_match.missing_requirements else 'None'}")
