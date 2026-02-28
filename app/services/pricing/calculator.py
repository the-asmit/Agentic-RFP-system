"""Pricing calculation service."""
from typing import List
from app.schemas.product import Product
from app.schemas.match import MatchResult
from app.schemas.pricing import PricingResult, TestCost
from app.services.loader import load_pricing_tests, load_config
from app.core.logging import logger


async def calculate_pricing(
    matches: List[MatchResult],
    products: List[Product]
) -> List[PricingResult]:
    """
    Calculate pricing for matched products.
    
    Formula: (base_price + test_costs) * (1 + markup_percentage/100)
    
    Args:
        matches: Matched products
        products: Full product list
        
    Returns:
        List of PricingResult objects
    """
    logger.info(f"Calculating pricing for {len(matches)} matched products")
    
    if not matches:
        logger.warning("Calculator: No matches provided")
        return []
    
    if not products:
        logger.error("Calculator: No products provided")
        return []
    
    try:
        # Load pricing data
        config = await load_config()
        pricing_tests = await load_pricing_tests()
        
        markup_percentage = config.get("markup_percentage", 25)
        default_tests = config.get("default_tests", ["security_audit", "integration_test"])
        
        logger.info(f"Markup percentage: {markup_percentage}%")
        logger.info(f"Default tests: {default_tests}")
        
        pricing_results = []
        
        for match in matches:
            # Find product
            product = next((p for p in products if p.id == match.product_id), None)
            if not product:
                logger.warning(f"Product not found: {match.product_id}")
                continue
            
            # Calculate test costs
            test_costs = []
            total_test_cost = 0
            
            for test_name in default_tests:
                test = next((t for t in pricing_tests if t.get("test_name") == test_name), None)
                if test:
                    test_cost = TestCost(
                        test_name=test.get("test_name", "Unknown Test"),
                        cost=test.get("cost", 0),
                        description=test.get("description", "")
                    )
                    test_costs.append(test_cost)
                    total_test_cost += test.get("cost", 0)
                else:
                    logger.warning(f"Pricing test not found: {test_name}")
            
            # Calculate totals
            subtotal = product.base_price + total_test_cost
            markup_amount = subtotal * (markup_percentage / 100)
            total_price = subtotal + markup_amount
            
            # Build breakdown
            breakdown = {
                "base_price": product.base_price,
                "test_costs": total_test_cost,
                "subtotal": subtotal,
                "markup": markup_amount,
                "total": total_price
            }
            
            pricing_result = PricingResult(
                product_id=product.id,
                product_name=product.name,
                base_price=product.base_price,
                test_costs=test_costs,
                total_test_cost=total_test_cost,
                subtotal=subtotal,
                markup_percentage=markup_percentage,
                markup_amount=markup_amount,
                total_price=total_price,
                breakdown=breakdown
            )
            
            pricing_results.append(pricing_result)
            logger.info(
                f"Pricing calculated for {product.name}: ${total_price:,.2f}"
            )
        
        logger.info(f"Pricing calculated for {len(pricing_results)} products")
        return pricing_results
    
    except Exception as e:
        logger.error(f"Calculator: Error calculating pricing - {str(e)}")
        raise
