import cv2
import numpy as np
import pytesseract
import logging
from pathlib import Path
from PIL import Image
import easyocr

class DocumentProcessor:
    """A class to handle document OCR processing with multiple OCR engines."""
    
    def __init__(self, ocr_engine='tesseract', lang='eng'):
        """
        Initialize the DocumentProcessor.
        
        Args:
            ocr_engine (str): OCR engine to use ('tesseract' or 'easyocr')
            lang (str): Language for OCR processing
        """
        self.ocr_engine = ocr_engine
        self.lang = lang
        self.logger = self._setup_logger()
        
        if ocr_engine == 'easyocr':
            self.reader = easyocr.Reader([lang])
        
    def _setup_logger(self):
        """Set up logging configuration."""
        logger = logging.getLogger('DocumentProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def preprocess_image(self, image):
        """
        Preprocess the image for better OCR results.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Preprocessed image
        """
        try:
            from src.vision.image_enhancement import (
                enhance_image,
                deskew_image,
                remove_background,
                auto_crop
            )
            
            # Enhance image quality
            enhanced = enhance_image(image)
            
            # Deskew if needed
            deskewed = deskew_image(enhanced)
            
            # Auto-crop to content
            cropped, _ = auto_crop(deskewed)
            
            # Remove background noise
            cleaned = remove_background(cropped)
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Error in image preprocessing: {str(e)}")
            raise
    
    def extract_text_tesseract(self, image):
        """Extract text using Tesseract OCR."""
        try:
            text = pytesseract.image_to_string(image, lang=self.lang)
            return text.strip()
        except Exception as e:
            self.logger.error(f"Tesseract OCR error: {str(e)}")
            raise
    
    def extract_text_easyocr(self, image):
        """Extract text using EasyOCR."""
        try:
            results = self.reader.readtext(image)
            text = ' '.join([result[1] for result in results])
            return text.strip()
        except Exception as e:
            self.logger.error(f"EasyOCR error: {str(e)}")
            raise
    
    def process(self, image_path):
        """
        Process an image and extract text.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text from the image
        """
        try:
            # Load image
            self.logger.info(f"Processing image: {image_path}")
            image_path = Path(image_path)
            
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Preprocess
            preprocessed = self.preprocess_image(image)
            
            # Extract text using selected OCR engine
            if self.ocr_engine == 'tesseract':
                text = self.extract_text_tesseract(preprocessed)
            else:
                text = self.extract_text_easyocr(preprocessed)
            
            self.logger.info("Text extraction completed successfully")
            return text
            
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            raise