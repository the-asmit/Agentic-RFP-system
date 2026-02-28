"""LangGraph workflow definition."""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.core.state import RFPState
from app.core.logging import logger


def create_rfp_graph() -> StateGraph:
    """
    Create the RFP processing workflow graph.
    
    Flow: START → match → select → pricing → agent → output → END
    
    Returns:
        Configured StateGraph
    """
    from app.services.matching.matcher import match_products_to_rfp
    from app.services.pricing.calculator import calculate_pricing
    from app.agents.orchestrator import run_agents
    from app.output.formatter import format_proposal
    
    # Define workflow nodes
    async def match_node(state: RFPState) -> Dict[str, Any]:
        """Match products to RFP requirements."""
        logger.info(f"Match node: Processing RFP {state['rfp_id']}")
        try:
            matches = await match_products_to_rfp(state["rfp"], state["products"])
            logger.info(f"Match node: Found {len(matches)} matches")
            
            if not matches:
                logger.warning("Match node: No products matched RFP requirements")
                return {
                    "matches": [],
                    "all_matches": [],
                    "error": "No suitable products found for the RFP requirements"
                }
            
            # Store all matches for later analysis
            return {
                "matches": matches,
                "all_matches": matches  # Keep all for rejection analysis
            }
        except Exception as e:
            logger.error(f"Match node: Error - {str(e)}")
            return {
                "matches": [],
                "all_matches": [],
                "error": f"Matching failed: {str(e)}"
            }
    
    async def select_node(state: RFPState) -> Dict[str, Any]:
        """Select the best product from matches and assess suitability."""
        from app.services.loader import load_config
        
        logger.info("Select node: Choosing best product")
        
        matches = state.get("matches", [])
        all_matches = state.get("all_matches", matches)
        
        if not matches:
            logger.warning("Select node: No matches to select from")
            return {
                "matches": [],
                "selection_justification": "No products matched the RFP requirements.",
                "suitability": "not suitable",
                "suitability_reason": "No products meet minimum requirements",
                "rejected_products": []
            }
        
        # Get threshold from config
        try:
            config = await load_config()
            threshold = config.get("matching_threshold", 0.3)
        except:
            threshold = 0.3
            logger.warning(f"Could not load config, using default threshold {threshold}")
        
        # Select product with highest match score (already sorted)
        best_match = matches[0]
        
        # Check if best match meets threshold
        if best_match.match_score < threshold:
            logger.warning(f"Select node: Best match score {best_match.match_score:.2f} below threshold {threshold}")
            return {
                "matches": [],
                "selection_justification": f"No suitable product found. Best match ({best_match.product_name}) scored {best_match.match_score:.2f}, below required threshold of {threshold:.2f}.",
                "suitability": "not suitable",
                "suitability_reason": f"Best match score ({best_match.match_score:.2f}) below threshold ({threshold:.2f})",
                "rejected_products": [],
                "error": "No suitable products meet the minimum requirements"
            }
        
        # Helper function to check for critical missing requirements
        def has_critical_missing_requirements(missing_reqs: list) -> tuple[bool, str]:
            """Check if missing requirements include critical ones."""
            if not missing_reqs:
                return False, ""
            
            critical_keywords = [
                "compliance", "compliant", "regulatory", "regulation",
                "security", "secure", "encryption", "authentication",
                "mandatory", "required", "must have", "critical",
                "certification", "certified", "audit", "sox", "hipaa", 
                "gdpr", "pci", "iso", "soc 2", "soc2"
            ]
            
            missing_lower = [req.lower() for req in missing_reqs]
            critical_missing = []
            
            for req in missing_lower:
                for keyword in critical_keywords:
                    if keyword in req:
                        # Find original casing
                        original_req = next((r for r in missing_reqs if r.lower() == req), req)
                        critical_missing.append(original_req)
                        break
            
            if critical_missing:
                return True, ", ".join(critical_missing[:3])
            return False, ""
        
        # Assess suitability
        score = best_match.match_score
        missing_reqs = best_match.missing_requirements or []
        has_critical, critical_items = has_critical_missing_requirements(missing_reqs)
        
        # Determine suitability classification
        if score >= 0.8 and not has_critical:
            suitability = "suitable"
            suitability_reason = f"Strong match ({int(score*100)}%) with no critical missing requirements"
        elif score >= 0.6 and not has_critical:
            suitability = "suitable"
            suitability_reason = f"Moderate match ({int(score*100)}%) with acceptable gaps"
        elif has_critical:
            suitability = "not suitable"
            suitability_reason = f"Missing critical requirements: {critical_items}"
        elif score < 0.6:
            suitability = "partial"
            suitability_reason = f"Weak match ({int(score*100)}%), significant gaps exist"
        else:
            suitability = "partial"
            suitability_reason = f"Moderate match ({int(score*100)}%) with some gaps"
        
        logger.info(f"Select node: Suitability = {suitability} - {suitability_reason}")
        
        # Create selection justification
        matched_reqs = ", ".join(best_match.matched_specs[:5]) if best_match.matched_specs else "None"
        missing_reqs_str = ", ".join(missing_reqs[:3]) if missing_reqs else "None"
        
        match_category = "Strong" if score >= 0.8 else "Moderate" if score >= 0.6 else "Weak"
        
        justification = (
            f"Selected: {best_match.product_name}\n"
            f"Match Score: {best_match.match_score:.2f} ({int(best_match.match_score*100)}%) - {match_category} Match\n"
            f"Key Matched Requirements: {matched_reqs}\n"
            f"Missing Requirements: {missing_reqs_str}"
        )
        
        # Create rejection reasons for other products
        rejected = []
        for match in all_matches[1:]:  # Skip the first (selected) product
            reason = f"Lower match score ({match.match_score:.2f})"
            if match.missing_requirements:
                key_missing = ", ".join(match.missing_requirements[:2])
                reason += f", missing: {key_missing}"
            
            rejected.append({
                "product_name": match.product_name,
                "match_score": match.match_score,
                "reason": reason
            })
        
        logger.info(f"Select node: Selected {best_match.product_name} with score {best_match.match_score:.2f}")
        logger.info(f"Select node: Rejected {len(rejected)} other products")
        
        return {
            "matches": [best_match],
            "selection_justification": justification,
            "suitability": suitability,
            "suitability_reason": suitability_reason,
            "rejected_products": rejected
        }
    
    async def pricing_node(state: RFPState) -> Dict[str, Any]:
        """Calculate pricing for matched products."""
        logger.info(f"Pricing node: Calculating for {len(state.get('matches', []))} products")
        
        matches = state.get("matches", [])
        if not matches:
            logger.warning("Pricing node: No matches to price")
            return {"pricing": []}
        
        try:
            pricing = await calculate_pricing(matches, state["products"])
            logger.info(f"Pricing node: Calculated {len(pricing)} pricing results")
            return {"pricing": pricing}
        except Exception as e:
            logger.error(f"Pricing node: Error - {str(e)}")
            return {
                "pricing": [],
                "error": f"Pricing calculation failed: {str(e)}"
            }
    
    async def agent_node(state: RFPState) -> Dict[str, Any]:
        """Run AI agents to generate explanations."""
        logger.info("Agent node: Running AI agents")
        
        matches = state.get("matches", [])
        pricing = state.get("pricing", [])
        suitability = state.get("suitability", "unknown")
        suitability_reason = state.get("suitability_reason", "")
        
        if not matches or not pricing:
            logger.warning("Agent node: Insufficient data for agent processing")
            return {
                "technical_analysis": "Insufficient data for technical analysis.",
                "pricing_explanation": "Insufficient data for pricing explanation.",
                "sales_pitch": "Unable to generate proposal due to insufficient data."
            }
        
        try:
            agent_results = await run_agents(
                state["rfp"],
                matches,
                pricing,
                suitability,
                suitability_reason
            )
            logger.info("Agent node: AI agents completed")
            return agent_results
        except Exception as e:
            logger.error(f"Agent node: Error - {str(e)}")
            return {
                "technical_analysis": f"Technical analysis error: {str(e)}",
                "pricing_explanation": f"Pricing explanation error: {str(e)}",
                "sales_pitch": f"Sales pitch generation error: {str(e)}"
            }
    
    async def output_node(state: RFPState) -> Dict[str, Any]:
        """Format final proposal."""
        logger.info("Output node: Formatting proposal")
        try:
            proposal = await format_proposal(state)
            logger.info(f"Output node: Proposal generated for RFP {state['rfp_id']}")
            return {"proposal": proposal}
        except Exception as e:
            logger.error(f"Output node: Error - {str(e)}")
            return {"error": f"Failed to format proposal: {str(e)}"}
    
    # Build graph
    workflow = StateGraph(RFPState)
    
    # Add nodes
    workflow.add_node("match", match_node)
    workflow.add_node("select", select_node)
    workflow.add_node("pricing", pricing_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("output", output_node)
    
    # Routing function to skip agents if no product selected
    def should_continue(state: RFPState) -> str:
        """Decide whether to continue to pricing or skip to output."""
        matches = state.get("matches", [])
        if not matches:
            logger.info("Router: No suitable product found, skipping to output")
            return "output"
        return "pricing"
    
    # Define edges
    workflow.set_entry_point("match")
    workflow.add_edge("match", "select")
    workflow.add_conditional_edges(
        "select",
        should_continue,
        {
            "pricing": "pricing",
            "output": "output"
        }
    )
    workflow.add_edge("pricing", "agent")
    workflow.add_edge("agent", "output")
    workflow.add_edge("output", END)
    
    logger.info("RFP workflow graph created")
    return workflow.compile()
