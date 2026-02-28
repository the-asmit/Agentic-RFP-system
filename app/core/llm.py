"""LLM initialization and configuration."""
from langchain_anthropic import ChatAnthropic
from app.core.config import settings
from app.core.logging import logger


def get_llm(temperature: float = 0.7) -> ChatAnthropic:
    """
    Get configured LLM instance.
    
    Args:
        temperature: LLM temperature (0-1)
        
    Returns:
        Configured ChatAnthropic instance
    """
    logger.info("Initializing Claude LLM")
    
    if not settings.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")
    
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        temperature=temperature,
        max_tokens=4096
    )
    
    logger.info(f"LLM initialized with model: claude-sonnet-4-20250514")
    return llm
