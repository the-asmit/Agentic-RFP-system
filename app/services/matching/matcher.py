"""Product matching service."""
from typing import List
from app.schemas.rfp import RFP
from app.schemas.product import Product
from app.schemas.match import MatchResult
from app.services.loader import load_config
from app.core.logging import logger


async def match_products_to_rfp(rfp: RFP, products: List[Product]) -> List[MatchResult]:
    """
    Match products to RFP requirements using keyword matching.
    
    Args:
        rfp: RFP to match against
        products: List of available products
        
    Returns:
        List of MatchResult objects sorted by match score
    """
    logger.info(f"Matching products for RFP: {rfp.id}")
    
    if not products:
        logger.warning("Matcher: No products available")
        return []
    
    if not rfp.requirements:
        logger.warning("Matcher: RFP has no requirements")
        return []
    
    try:
        config = await load_config()
        threshold = config.get("matching_threshold", 0.3)
        
        logger.info(f"Matching threshold: {threshold}")
        
        matches = []
        
        for product in products:
            match_result = _calculate_match(rfp, product)
            
            if match_result.match_score >= threshold:
                matches.append(match_result)
                logger.info(
                    f"Product {product.id} matched with score {match_result.match_score:.2f}"
                )
        
        # Sort by match score descending
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        logger.info(f"Total matches found: {len(matches)}")
        return matches
    
    except Exception as e:
        logger.error(f"Matcher: Error during matching - {str(e)}")
        raise


def _calculate_match(rfp: RFP, product: Product) -> MatchResult:
    """
    Calculate match score between RFP and product.
    
    Uses simple keyword matching - counts how many RFP requirements
    are found in product specs (case-insensitive, partial matching).
    
    Args:
        rfp: RFP with requirements
        product: Product with specs
        
    Returns:
        MatchResult with score and details
    """
    matched_specs = []
    missing_requirements = []
    
    # Normalize for comparison
    product_specs_lower = [spec.lower() for spec in product.specs]
    product_specs_text = " ".join(product_specs_lower)
    
    for requirement in rfp.requirements:
        requirement_lower = requirement.lower()
        
        # Check if any product spec contains the requirement keywords
        matched = False
        for spec in product.specs:
            if _keyword_match(requirement_lower, spec.lower()):
                matched_specs.append(spec)
                matched = True
                break
        
        if not matched:
            # Check if requirement words appear in any spec
            req_words = requirement_lower.split()
            for word in req_words:
                if len(word) > 3 and word in product_specs_text:
                    # Found at least one significant word
                    for spec in product.specs:
                        if word in spec.lower():
                            matched_specs.append(spec)
                            matched = True
                            break
                    if matched:
                        break
        
        if not matched:
            missing_requirements.append(requirement)
    
    # Calculate score
    total_requirements = len(rfp.requirements)
    matched_count = total_requirements - len(missing_requirements)
    match_score = matched_count / total_requirements if total_requirements > 0 else 0
    
    # Remove duplicates from matched specs
    matched_specs = list(set(matched_specs))
    
    return MatchResult(
        product_id=product.id,
        product_name=product.name,
        match_score=round(match_score, 2),
        matched_specs=matched_specs,
        missing_requirements=missing_requirements
    )


def _keyword_match(requirement: str, spec: str) -> bool:
    """
    Check if requirement matches spec using keyword matching.
    
    Args:
        requirement: RFP requirement (lowercase)
        spec: Product spec (lowercase)
        
    Returns:
        True if there's a match
    """
    # Direct substring match
    if requirement in spec or spec in requirement:
        return True
    
    # Check if significant words overlap
    req_words = set(requirement.split())
    spec_words = set(spec.split())
    
    # Remove common words
    common_words = {'the', 'and', 'or', 'for', 'with', 'support', 'system', 'a', 'an'}
    req_words -= common_words
    spec_words -= common_words
    
    # Check for overlap
    overlap = req_words & spec_words
    
    # Match if at least 2 significant words overlap, or 1 word for short requirements
    min_overlap = 1 if len(req_words) <= 2 else 2
    return len(overlap) >= min_overlap
