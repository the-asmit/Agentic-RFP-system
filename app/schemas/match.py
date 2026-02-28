"""Match result schema definitions."""
from typing import List
from pydantic import BaseModel, Field


class MatchResult(BaseModel):
    """Product matching result."""
    
    product_id: str = Field(..., description="Matched product ID")
    product_name: str = Field(..., description="Matched product name")
    match_score: float = Field(..., description="Match score (0-1)")
    matched_specs: List[str] = Field(..., description="Specifications that matched")
    missing_requirements: List[str] = Field(
        default_factory=list,
        description="RFP requirements not met"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod-001",
                "product_name": "CloudGuard Firewall Pro",
                "match_score": 0.85,
                "matched_specs": ["firewall", "VPN", "intrusion prevention"],
                "missing_requirements": []
            }
        }
