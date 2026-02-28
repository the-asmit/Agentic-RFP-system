"""Pricing schema definitions."""
from typing import List, Dict
from pydantic import BaseModel, Field


class TestCost(BaseModel):
    """Test cost item."""
    
    test_name: str = Field(..., description="Test name")
    cost: float = Field(..., description="Test cost in USD")
    description: str = Field(..., description="Test description")


class PricingResult(BaseModel):
    """Pricing calculation result."""
    
    product_id: str = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    base_price: float = Field(..., description="Base product price")
    test_costs: List[TestCost] = Field(
        default_factory=list,
        description="Testing costs"
    )
    total_test_cost: float = Field(0, description="Sum of test costs")
    subtotal: float = Field(..., description="Base + tests")
    markup_percentage: float = Field(..., description="Markup percentage")
    markup_amount: float = Field(..., description="Markup amount")
    total_price: float = Field(..., description="Final total price")
    breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Detailed price breakdown"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod-001",
                "product_name": "CloudGuard Firewall Pro",
                "base_price": 15000,
                "total_test_cost": 4000,
                "subtotal": 19000,
                "markup_percentage": 25,
                "markup_amount": 4750,
                "total_price": 23750
            }
        }
