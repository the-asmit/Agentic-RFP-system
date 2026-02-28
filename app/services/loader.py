"""Data loader service."""
import json
from typing import List, Dict, Any
from pathlib import Path
from app.schemas.rfp import RFP
from app.schemas.product import Product
from app.core.config import settings
from app.core.logging import logger


async def load_rfp(rfp_id: str) -> RFP:
    """
    Load RFP from file.
    
    Args:
        rfp_id: RFP identifier (e.g., 'rfp1')
        
    Returns:
        RFP object
        
    Raises:
        FileNotFoundError: If RFP file doesn't exist
        ValueError: If RFP data is invalid
    """
    rfp_file = settings.RFP_DIR / f"{rfp_id}.json"
    
    if not rfp_file.exists():
        logger.error(f"RFP file not found: {rfp_file}")
        raise FileNotFoundError(f"RFP file not found: {rfp_id}")
    
    logger.info(f"Loading RFP from {rfp_file}")
    
    try:
        with open(rfp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        rfp = RFP(**data)
        logger.info(f"RFP loaded: {rfp.id} - {rfp.title}")
        return rfp
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in RFP file {rfp_file}: {str(e)}")
        raise ValueError(f"Invalid JSON in RFP file: {rfp_id}")
    except Exception as e:
        logger.error(f"Error loading RFP {rfp_id}: {str(e)}")
        raise ValueError(f"Failed to load RFP: {str(e)}")


async def load_products() -> List[Product]:
    """
    Load all products from file.
    
    Returns:
        List of Product objects
    """
    logger.info(f"Loading products from {settings.PRODUCTS_FILE}")
    
    try:
        if not settings.PRODUCTS_FILE.exists():
            logger.error(f"Products file not found: {settings.PRODUCTS_FILE}")
            raise FileNotFoundError("Products file not found")
        
        with open(settings.PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error("Products file must contain a list")
            raise ValueError("Products file must contain a list")
        
        products = [Product(**item) for item in data]
        logger.info(f"Loaded {len(products)} products")
        return products
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in products file: {str(e)}")
        raise ValueError("Invalid JSON in products file")
    except Exception as e:
        logger.error(f"Error loading products: {str(e)}")
        raise


async def load_pricing_tests() -> List[Dict[str, Any]]:
    """
    Load pricing test configurations.
    
    Returns:
        List of pricing test dictionaries
    """
    logger.info(f"Loading pricing tests from {settings.PRICING_FILE}")
    
    try:
        if not settings.PRICING_FILE.exists():
            logger.warning(f"Pricing file not found: {settings.PRICING_FILE}, using empty list")
            return []
        
        with open(settings.PRICING_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error("Pricing file must contain a list")
            raise ValueError("Pricing file must contain a list")
        
        logger.info(f"Loaded {len(data)} pricing tests")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in pricing file: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error loading pricing tests: {str(e)}")
        return []


async def load_config() -> Dict[str, Any]:
    """
    Load system configuration.
    
    Returns:
        Configuration dictionary
    """
    logger.info(f"Loading config from {settings.CONFIG_FILE}")
    
    try:
        if not settings.CONFIG_FILE.exists():
            logger.warning(f"Config file not found: {settings.CONFIG_FILE}, using defaults")
            return {
                "matching_threshold": 0.3,
                "markup_percentage": 25,
                "default_tests": ["security_audit", "integration_test"]
            }
        
        with open(settings.CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info("Configuration loaded")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {str(e)}")
        return {
            "matching_threshold": 0.3,
            "markup_percentage": 25,
            "default_tests": ["security_audit", "integration_test"]
        }
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return {
            "matching_threshold": 0.3,
            "markup_percentage": 25,
            "default_tests": ["security_audit", "integration_test"]
        }
