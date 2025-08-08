"""
Core module for SlideSage PowerPoint inconsistency detection.
"""

from .extractor import TextExtractor
from .analyzer import GeminiAnalyzer
from .detector import InconsistencyDetector
from .output import OutputFormatter

__all__ = ['TextExtractor', 'GeminiAnalyzer', 'InconsistencyDetector', 'OutputFormatter'] 