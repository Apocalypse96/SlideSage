"""
OCR utilities for extracting text from slide images.
"""

import os
import logging
from typing import Optional, Tuple, List
from pathlib import Path

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("OCR dependencies not available. Install pytesseract and Pillow for OCR support.")


class OCRProcessor:
    """Handles OCR text extraction from images."""
    
    def __init__(self, confidence_threshold: int = 70):
        """
        Initialize OCR processor.
        
        Args:
            confidence_threshold: Minimum confidence score for OCR results (0-100)
        """
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        if not OCR_AVAILABLE:
            self.logger.warning("OCR functionality not available. Install pytesseract and Pillow.")
    
    def extract_text_from_image(self, image_path: Path) -> Tuple[str, float]:
        """
        Extract text from an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not OCR_AVAILABLE:
            return "", 0.0
        
        try:
            # Load and preprocess image
            image = self._load_and_preprocess_image(image_path)
            
            # Extract text with confidence scores
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Filter results by confidence
            text_parts = []
            total_confidence = 0
            valid_words = 0
            
            for i, confidence in enumerate(data['conf']):
                if confidence > self.confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        total_confidence += confidence
                        valid_words += 1
            
            extracted_text = ' '.join(text_parts)
            avg_confidence = total_confidence / valid_words if valid_words > 0 else 0.0
            
            self.logger.debug(f"OCR extracted {len(text_parts)} words with avg confidence {avg_confidence:.1f}%")
            
            return extracted_text, avg_confidence
            
        except Exception as e:
            self.logger.error(f"OCR failed for {image_path}: {str(e)}")
            return "", 0.0
    
    def extract_text_from_pil_image(self, image) -> Tuple[str, float]:
        """
        Extract text from a PIL Image object.
        
        Args:
            image: PIL Image object
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not OCR_AVAILABLE:
            return "", 0.0
        
        try:
            # Preprocess the image
            processed_image = self._preprocess_image(image)
            
            # Extract text with confidence scores
            data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            
            # Filter results by confidence
            text_parts = []
            total_confidence = 0
            valid_words = 0
            
            for i, confidence in enumerate(data['conf']):
                if confidence > self.confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        total_confidence += confidence
                        valid_words += 1
            
            extracted_text = ' '.join(text_parts)
            avg_confidence = total_confidence / valid_words if valid_words > 0 else 0.0
            
            return extracted_text, avg_confidence
            
        except Exception as e:
            self.logger.error(f"OCR failed for PIL image: {str(e)}")
            return "", 0.0
    
    def _load_and_preprocess_image(self, image_path: Path):
        """Load and preprocess image for better OCR results."""
        # Load image
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return self._preprocess_image(image)
    
    def _preprocess_image(self, image):
        """Apply preprocessing techniques to improve OCR accuracy."""
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def is_available(self) -> bool:
        """Check if OCR functionality is available."""
        return OCR_AVAILABLE
    
    def get_tesseract_version(self) -> Optional[str]:
        """Get Tesseract version if available."""
        if not OCR_AVAILABLE:
            return None
        
        try:
            return pytesseract.get_tesseract_version()
        except Exception:
            return None
    
    def set_tesseract_path(self, path: str):
        """Set custom Tesseract executable path."""
        if OCR_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = path
            self.logger.info(f"Set Tesseract path to: {path}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported OCR languages."""
        if not OCR_AVAILABLE:
            return []
        
        try:
            return pytesseract.get_languages()
        except Exception as e:
            self.logger.error(f"Failed to get supported languages: {str(e)}")
            return []
    
    def extract_text_with_language(self, image_path: Path, language: str = 'eng') -> Tuple[str, float]:
        """
        Extract text with specified language.
        
        Args:
            image_path: Path to the image file
            language: Language code (e.g., 'eng', 'fra', 'deu')
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not OCR_AVAILABLE:
            return "", 0.0
        
        try:
            image = self._load_and_preprocess_image(image_path)
            
            # Extract text with specified language
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Filter results by confidence
            text_parts = []
            total_confidence = 0
            valid_words = 0
            
            for i, confidence in enumerate(data['conf']):
                if confidence > self.confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        total_confidence += confidence
                        valid_words += 1
            
            extracted_text = ' '.join(text_parts)
            avg_confidence = total_confidence / valid_words if valid_words > 0 else 0.0
            
            return extracted_text, avg_confidence
            
        except Exception as e:
            self.logger.error(f"OCR failed for {image_path} with language {language}: {str(e)}")
            return "", 0.0 