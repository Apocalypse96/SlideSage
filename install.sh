#!/bin/bash
# SlideSage Installation Script

echo "🎯 Installing SlideSage - PowerPoint Intelligence Analysis Tool"
echo "================================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check for Tesseract OCR
echo "🔍 Checking for Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR found: $(tesseract --version | head -n1)"
else
    echo "⚠️  Tesseract OCR not found. Installing..."
    
    # Detect OS and install Tesseract
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install tesseract
        else
            echo "❌ Homebrew not found. Please install Tesseract manually:"
            echo "   Visit: https://github.com/tesseract-ocr/tesseract"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y tesseract-ocr
        elif command -v yum &> /dev/null; then
            sudo yum install -y tesseract
        else
            echo "❌ Package manager not found. Please install Tesseract manually."
        fi
    else
        echo "❌ Unsupported OS. Please install Tesseract manually."
    fi
fi

# Make slide_sage.py executable
chmod +x slide_sage.py

echo ""
echo "🎉 SlideSage installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Set up your Gemini API key:"
echo "   - Get your key from: https://aistudio.google.com/app/apikey"
echo "   - Copy env.example to .env and add your key"
echo ""
echo "2. Test the installation:"
echo "   python3 slide_sage.py --help"
echo ""
echo "3. Analyze a presentation:"
echo "   python3 slide_sage.py your_presentation.pptx"
echo ""
echo "📚 For more information, see README.md" 