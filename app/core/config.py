"""Configuration management."""
import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings."""
    
    # API Settings
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RFP_DIR: Path = DATA_DIR / "rfps"
    LOGS_DIR: Path = BASE_DIR / "logs"
    OUTPUT_DIR: Path = BASE_DIR / "output"
    
    # Data files
    PRODUCTS_FILE: Path = DATA_DIR / "products.json"
    PRICING_FILE: Path = DATA_DIR / "pricing.json"
    CONFIG_FILE: Path = DATA_DIR / "config.json"
    
    # Ensure directories exist
    def __init__(self):
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
    
    def validate(self) -> bool:
        """Validate critical settings."""
        if not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment")
        return True


settings = Settings()
