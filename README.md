# SlideSage - PowerPoint Inconsistency Detector

A robust Python command-line tool that analyzes multi-slide PowerPoint decks (`.pptx` files) and automatically detects cross-slide factual or logical inconsistencies.



https://github.com/user-attachments/assets/68dcc86f-4757-4d18-800b-df10c971c7df






## Features

- **Comprehensive Text Extraction**: Extracts text from all slide elements using `python-pptx`
- **OCR Support**: Uses `pytesseract` for extracting text from image-only slides
- **AI-Powered Analysis**: Leverages Google's Gemini 2.5 Flash LLM for intelligent inconsistency detection
- **Multiple Inconsistency Types**: Detects numerical conflicts, contradictory statements, timeline mismatches, and logical inconsistencies
- **Structured Output**: Provides clear, categorized results with specific slide references
- **Scalable Design**: Handles large decks (50+ slides) efficiently with modular architecture

## Installation

### Quick Start (Recommended)

1. **Clone this repository**:
   ```bash
   git clone (https://github.com/Apocalypse96/SlideSage.git)
   cd SlideSage
   ```

2. **Run the installation script**:
   ```bash
   ./install.sh
   ```

3. **Set up your Gemini API key**:
   ```bash
   cp env.example .env
   # Edit .env and add your API key
   ```
   
   Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Manual Installation

If you prefer manual installation:

1. **Prerequisites**:
   - **Python 3.8+** installed on your system
   - **Tesseract OCR** installed:
     - **macOS**: `brew install tesseract`
     - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
     - **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Gemini API key**:
   ```bash
   cp env.example .env
   # Edit .env and add your API key
   ```

## Usage

### Basic Usage

```bash
python slide_sage.py path/to/presentation.pptx
```

### Advanced Usage

```bash
# Analyze with custom output format
python slide_sage.py presentation.pptx --output-format yaml

# Set custom confidence threshold for OCR
python slide_sage.py presentation.pptx --ocr-confidence 60

# Enable verbose logging
python slide_sage.py presentation.pptx --verbose

# Analyze with specific slide range
python slide_sage.py presentation.pptx --start-slide 5 --end-slide 20
```

### Command Line Options

- `--output-format`: Output format (yaml, markdown, text) [default: yaml]
- `--ocr-confidence`: OCR confidence threshold (0-100) [default: 70]
- `--verbose`: Enable verbose logging
- `--start-slide`: First slide to analyze (1-based)
- `--end-slide`: Last slide to analyze (1-based)
- `--max-tokens`: Maximum tokens for Gemini API calls [default: 4000]

## Detection Approach

### 1. Text Extraction
- **Structured Content**: Extracts text from titles, body text, tables, and shapes using `python-pptx`
- **Image Content**: Uses OCR to extract text from slide images when structured text is insufficient
- **Fallback Strategy**: If OCR fails, logs the issue and continues with other slides

### 2. Content Analysis
- **Data Aggregation**: Collects all extracted text, numbers, dates, and claims
- **Categorization**: Groups content by type (numerical data, statements, timelines)
- **Context Preservation**: Maintains slide numbers and content context

### 3. AI-Powered Comparison
- **Gemini 2.5 Flash**: Uses Google's advanced LLM for intelligent inconsistency detection
- **Cross-Slide Analysis**: Compares content across all slides for conflicts
- **Logical Reasoning**: Identifies contradictions, timeline issues, and factual inconsistencies

### 4. Inconsistency Types Detected

#### Numerical Conflicts
- Revenue figures that don't match across slides
- Percentage calculations that are inconsistent
- Quantity discrepancies in data presentations

#### Contradictory Statements
- Opposing claims about market conditions
- Conflicting strategic statements
- Inconsistent competitive analysis

#### Timeline/Date Issues
- Forecast contradictions
- Historical date mismatches
- Project timeline inconsistencies

#### Logical Inconsistencies
- Arguments that contradict each other
- Inconsistent assumptions
- Logical fallacies in reasoning

## Output Format

The tool provides structured output with the following sections:

```yaml
summary:
  total_slides: 25
  slides_analyzed: 25
  inconsistencies_found: 3
  analysis_time: "2.5s"

inconsistencies:
  numerical_conflicts:
    - slide_numbers: [5, 12]
      description: "Revenue figures conflict: $1.2M vs $1.5M"
      severity: "high"
  
  contradictory_statements:
    - slide_numbers: [8, 15]
      description: "Market described as 'highly competitive' vs 'few competitors'"
      severity: "medium"
  
  timeline_issues:
    - slide_numbers: [3, 18]
      description: "Project completion dates don't align"
      severity: "high"
```

## Architecture

```
SlideSage/
├── slide_sage.py          # Main CLI entry point
├── core/
│   ├── __init__.py
│   ├── extractor.py       # Text extraction logic
│   ├── analyzer.py        # AI analysis engine
│   ├── detector.py        # Inconsistency detection
│   └── output.py          # Output formatting
├── utils/
│   ├── __init__.py
│   ├── ocr.py            # OCR utilities
│   └── helpers.py        # Helper functions
├── requirements.txt
├── .env.example
└── README.md
```

## Error Handling

The tool implements robust error handling:

- **OCR Failures**: Logs errors and continues with other slides
- **API Rate Limits**: Implements exponential backoff for Gemini API calls
- **File Access Issues**: Graceful handling of corrupted or inaccessible files
- **Memory Management**: Efficient processing of large presentations

## Limitations

### Current Limitations
- **Image Quality**: OCR accuracy depends on image quality and text clarity
- **Language Support**: Currently optimized for English text
- **Complex Layouts**: May miss text in complex graphical layouts
- **API Dependencies**: Requires internet connection for Gemini API calls

### Future Enhancements
- Multi-language OCR support
- Advanced layout analysis
- Offline analysis capabilities
- Integration with other LLM providers
- Real-time collaboration features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section in this README
2. Review existing GitHub issues
3. Create a new issue with detailed information about your problem

## Acknowledgments

- [python-pptx](https://github.com/scanny/python-pptx) for PowerPoint parsing
- [pytesseract](https://github.com/madmaze/pytesseract) for OCR capabilities
- [Google Gemini](https://ai.google.dev/) for AI-powered analysis 
