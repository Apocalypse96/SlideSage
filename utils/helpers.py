"""
Helper functions for SlideSage.
"""

import os
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('slide_sage.log')
        ]
    )
    return logging.getLogger(__name__)


def validate_file_path(file_path: str) -> Path:
    """Validate and return Path object for the input file."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    if path.suffix.lower() != '.pptx':
        raise ValueError(f"File must be a PowerPoint presentation (.pptx): {file_path}")
    
    return path


def extract_numbers_and_dates(text: str) -> Dict[str, List[Any]]:
    """
    Extract numbers, percentages, currency amounts, and dates from text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary with extracted data categorized by type
    """
    if not text:
        return {'numbers': [], 'percentages': [], 'currency': [], 'dates': []}
    
    # Currency patterns (e.g., $1,234.56, €1,000, £500)
    currency_pattern = r'[\$€£¥₹]\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
    currency_matches = re.findall(currency_pattern, text, re.IGNORECASE)
    
    # Percentage patterns (e.g., 25%, 12.5%)
    percentage_pattern = r'\d+(?:\.\d+)?\s*%'
    percentage_matches = re.findall(percentage_pattern, text, re.IGNORECASE)
    
    # Number patterns (integers and decimals)
    number_pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?\b'
    number_matches = re.findall(number_pattern, text)
    
    # Date patterns (various formats)
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY, DD/MM/YYYY
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
        r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',    # DD Month YYYY
    ]
    
    date_matches = []
    for pattern in date_patterns:
        date_matches.extend(re.findall(pattern, text, re.IGNORECASE))
    
    return {
        'numbers': number_matches,
        'percentages': percentage_matches,
        'currency': currency_matches,
        'dates': date_matches
    }


def clean_text(text: str) -> str:
    """Clean and normalize text for analysis."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might interfere with analysis
    text = re.sub(r'[^\w\s\.\,\%\$\€\£\¥\₹\-\(\)]', '', text)
    
    return text


def chunk_text(text: str, max_length: int = 1000) -> List[str]:
    """Split text into chunks for API processing."""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    sentences = re.split(r'[.!?]+', text)
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity using word overlap."""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes."""
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0


def create_backup_path(original_path: Path) -> Path:
    """Create a backup path for the original file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{original_path.stem}_backup_{timestamp}{original_path.suffix}"
    return original_path.parent / backup_name 