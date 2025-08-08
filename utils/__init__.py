"""
Utility modules for SlideSage PowerPoint inconsistency detection.
"""

from .ocr import OCRProcessor
from .helpers import setup_logging, validate_file_path, extract_numbers_and_dates

__all__ = ['OCRProcessor', 'setup_logging', 'validate_file_path', 'extract_numbers_and_dates'] 