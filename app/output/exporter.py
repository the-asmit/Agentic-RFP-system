"""Proposal exporter."""
import json
from pathlib import Path
from app.schemas.proposal import Proposal
from app.core.config import settings
from app.core.logging import logger


async def export_proposal(proposal: Proposal, output_dir: Path = None) -> Path:
    """
    Export proposal to JSON file.
    
    Args:
        proposal: Proposal to export
        output_dir: Output directory (default: settings.OUTPUT_DIR)
        
    Returns:
        Path to exported file
    """
    if output_dir is None:
        output_dir = settings.OUTPUT_DIR
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename
    filename = f"proposal_{proposal.rfp_id}_{datetime_to_filename(proposal.generated_at)}.json"
    output_path = output_dir / filename
    
    logger.info(f"Exporter: Writing proposal to {output_path}")
    
    # Convert to dict and write
    proposal_dict = proposal.model_dump()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(proposal_dict, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Exporter: Proposal exported to {output_path}")
    
    return output_path


def datetime_to_filename(iso_datetime: str) -> str:
    """Convert ISO datetime to filename-safe string."""
    # Replace problematic characters
    return iso_datetime.replace(":", "-").replace(".", "-").split("Z")[0]
