"""Pricing explanation agent."""
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.pricing import PricingResult
from app.core.llm import get_llm
from app.core.logging import logger


PRICING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a pricing analyst explaining cost breakdown.

Your job is to:
1. Explain the pricing components (base price, testing, markup)
2. Present the breakdown clearly
3. State the total cost

 CRITICAL RULES - NO EXCEPTIONS 

1. Use ONLY the provided pricing data - do NOT add or infer anything

2. DO NOT invent value propositions, ROI claims, or cost comparisons

3. DO NOT create fake cost savings or statistics

4. DO NOT mention features or capabilities not in the data

5. Be factual and concise

REMEMBER: Only explain the pricing numbers provided. Nothing more."""),
    ("user", """Explain the pricing for this product.

Product: {product_name}
Base Price: ${base_price:,.2f}
Test Costs: ${test_costs:,.2f}
Subtotal: ${subtotal:,.2f}
Markup ({markup_pct}%): ${markup:,.2f}
Total Price: ${total_price:,.2f}

Provide a clear pricing explanation using ONLY the data above. Do not add anything else.""")
])


async def explain_pricing(pricing: List[PricingResult]) -> str:
    """
    Generate pricing explanation for the best product.
    
    Args:
        pricing: List containing pricing for the single best product
        
    Returns:
        Pricing explanation text
    """
    logger.info("Pricing agent: Starting explanation")
    
    if not pricing:
        return "No pricing information available."
    
    # Work with the single product pricing
    best_pricing = pricing[0]
    
    try:
        llm = get_llm(temperature=0.3)  
        
        # Generate explanation
        chain = PRICING_PROMPT | llm
        response = await chain.ainvoke({
            "product_name": best_pricing.product_name,
            "base_price": best_pricing.base_price,
            "test_costs": best_pricing.total_test_cost,
            "subtotal": best_pricing.subtotal,
            "markup_pct": best_pricing.markup_percentage,
            "markup": best_pricing.markup_amount,
            "total_price": best_pricing.total_price
        })
        
        explanation = response.content
        logger.info(f"Pricing agent: Explanation generated ({len(explanation)} chars)")
        
        return explanation
    
    except Exception as e:
        logger.error(f"Pricing agent: Error generating explanation - {str(e)}")
        # Return fallback explanation
        return (f"Pricing for {best_pricing.product_name}:\n"
                f"Base Price: ${best_pricing.base_price:,.2f}\n"
                f"Testing Costs: ${best_pricing.total_test_cost:,.2f}\n"
                f"Markup ({best_pricing.markup_percentage}%): ${best_pricing.markup_amount:,.2f}\n"
                f"Total: ${best_pricing.total_price:,.2f}")
