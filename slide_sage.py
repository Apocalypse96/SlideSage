#!/usr/bin/env python3
"""
SlideSage - PowerPoint Inconsistency Detector

A robust Python command-line tool that analyzes multi-slide PowerPoint decks
and automatically detects cross-slide factual or logical inconsistencies.
"""

import sys
import time
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core import TextExtractor, GeminiAnalyzer, InconsistencyDetector, OutputFormatter
from utils import setup_logging, validate_file_path


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SlideSage - PowerPoint Inconsistency Detector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python slide_sage.py presentation.pptx
  python slide_sage.py presentation.pptx --output-format markdown
  python slide_sage.py presentation.pptx --ocr-confidence 80 --verbose
  python slide_sage.py presentation.pptx --start-slide 5 --end-slide 20
        """
    )
    
    parser.add_argument(
        'filename',
        help='Path to the PowerPoint presentation file (.pptx)'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['yaml', 'markdown', 'text'],
        default='yaml',
        help='Output format for results (default: yaml)'
    )
    
    parser.add_argument(
        '--ocr-confidence',
        type=int,
        default=70,
        metavar='0-100',
        help='OCR confidence threshold (default: 70)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--start-slide',
        type=int,
        metavar='N',
        help='First slide to analyze (1-based, default: 1)'
    )
    
    parser.add_argument(
        '--end-slide',
        type=int,
        metavar='N',
        help='Last slide to analyze (1-based, default: all slides)'
    )
    
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=4000,
        metavar='N',
        help='Maximum tokens for Gemini API calls (default: 4000)'
    )
    
    parser.add_argument(
        '--api-key',
        help='Gemini API key (if not set, will use GEMINI_API_KEY environment variable)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for SlideSage."""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    logger.info("Starting SlideSage PowerPoint Inconsistency Detector")
    
    try:
        # Validate input file
        pptx_path = validate_file_path(args.filename)
        logger.info(f"Analyzing presentation: {pptx_path}")
        
        # Initialize components
        extractor = TextExtractor(ocr_confidence=args.ocr_confidence)
        analyzer = GeminiAnalyzer(api_key=args.api_key, max_tokens=args.max_tokens)
        detector = InconsistencyDetector()
        formatter = OutputFormatter()
        
        # Check if required components are available
        if not extractor.is_available():
            error_msg = "PowerPoint parsing not available. Install python-pptx: pip install python-pptx"
            logger.error(error_msg)
            print(formatter.format_error(error_msg, args.output_format))
            sys.exit(1)
        
        if not analyzer.api_key:
            error_msg = "Gemini API key not found. Set GEMINI_API_KEY environment variable or use --api-key"
            logger.error(error_msg)
            print(formatter.format_error(error_msg, args.output_format))
            sys.exit(1)
        
        # Start analysis timer
        start_time = time.time()
        
        # Extract text from presentation
        logger.info("Extracting text from presentation...")
        slides_data = extractor.extract_from_presentation(pptx_path)
        
        if not slides_data:
            error_msg = "No slides found or failed to extract text from presentation"
            logger.error(error_msg)
            print(formatter.format_error(error_msg, args.output_format))
            sys.exit(1)
        
        # Filter slides if range specified
        if args.start_slide or args.end_slide:
            filtered_slides = {}
            start = args.start_slide or 1
            end = args.end_slide or max(slides_data.keys())
            
            for slide_num, slide_data in slides_data.items():
                if start <= slide_num <= end:
                    filtered_slides[slide_num] = slide_data
            
            slides_data = filtered_slides
            logger.info(f"Analyzing slides {start} to {end} (filtered from {len(slides_data)} slides)")
        
        # Get extraction summary
        extraction_summary = extractor.get_slide_summary(slides_data)
        logger.info(f"Extracted text from {extraction_summary['total_slides']} slides")
        logger.info(f"Found {extraction_summary['unique_numbers']} numbers, "
                   f"{extraction_summary['unique_percentages']} percentages, "
                   f"{extraction_summary['unique_currency']} currency amounts, "
                   f"{extraction_summary['unique_dates']} dates")
        
        # Analyze with AI
        logger.info("Analyzing content with Gemini AI...")
        ai_analysis = analyzer.analyze_inconsistencies(slides_data)
        
        if 'error' in ai_analysis:
            logger.warning(f"AI analysis had issues: {ai_analysis['error']}")
            # Continue with rule-based detection only
            results = detector.detect_inconsistencies(slides_data, {})
        else:
            # Check if we got intelligence-level analysis
            if ai_analysis.get('analysis_type') == 'intelligence':
                logger.info("Intelligence-level analysis detected")
                # Use intelligence report directly
                results = ai_analysis['intelligence_report']
            else:
                logger.info("Legacy analysis detected, running rule-based detection")
                # Use legacy format with rule-based detection
                results = detector.detect_inconsistencies(slides_data, ai_analysis)
        
        # Calculate analysis time
        analysis_time = time.time() - start_time
        
        # Format and output results
        logger.info("Formatting results...")
        output = formatter.format_results(results, args.output_format, analysis_time)
        
        # Print results
        print(output)
        
        # Log summary
        summary = results.get('summary', {})
        logger.info(f"Analysis completed in {analysis_time:.2f}s")
        logger.info(f"Found {summary.get('inconsistencies_found', 0)} inconsistencies")
        
        # Exit with appropriate code
        if summary.get('inconsistencies_found', 0) > 0:
            sys.exit(0)  # Inconsistencies found - normal exit
        else:
            sys.exit(0)  # No inconsistencies found - normal exit
            
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        print("\nAnalysis interrupted by user.")
        sys.exit(130)
        
    except FileNotFoundError as e:
        error_msg = f"File not found: {e}"
        logger.error(error_msg)
        formatter = OutputFormatter()
        print(formatter.format_error(error_msg, args.output_format))
        sys.exit(1)
        
    except ValueError as e:
        error_msg = f"Invalid input: {e}"
        logger.error(error_msg)
        formatter = OutputFormatter()
        print(formatter.format_error(error_msg, args.output_format))
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg, exc_info=True)
        formatter = OutputFormatter()
        print(formatter.format_error(error_msg, args.output_format))
        sys.exit(1)


if __name__ == '__main__':
    main() 