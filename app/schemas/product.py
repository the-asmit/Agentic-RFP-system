"""Product schema definitions."""
from typing import List
from pydantic import BaseModel, Field


class Product(BaseModel):
    """Product model."""
    
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    specs: List[str] = Field(..., description="Product specifications")
    base_price: float = Field(..., description="Base price in USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "prod-001",
                "name": "CloudGuard Firewall Pro",
                "specs": ["next-generation firewall", "VPN support"],
                "base_price": 15000
            }
        }
