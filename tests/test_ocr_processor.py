import os
import pytest
from pathlib import Path
import cv2
import numpy as np

from src.ocr.processor import DocumentProcessor
from src.vision.contour_detector import ContourDetector
from src.ocr.data_extractor import DataExtractor

# Fixture for sample image
@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    # Create a white image with black text
    img = np.ones((300, 500), dtype=np.uint8) * 255
    
    # Add some text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'Test Document', (50, 50), font, 1, (0, 0, 0), 2)
    cv2.putText(img, 'ID: DOC123', (50, 100), font, 1, (0, 0, 0), 2)
    cv2.putText(img, 'Date: 01/01/2025', (50, 150), font, 1, (0, 0, 0), 2)
    
    return img

# Fixture for temporary image file
@pytest.fixture
def temp_image_path(sample_image, tmp_path):
    """Save sample image to temporary file."""
    image_path = tmp_path / "test_doc.png"
    cv2.imwrite(str(image_path), sample_image)
    return str(image_path)

def test_document_processor_initialization():
    """Test DocumentProcessor initialization."""
    processor = DocumentProcessor()
    assert processor.ocr_engine == 'tesseract'
    assert processor.lang == 'eng'

def test_document_processor_preprocess_image(sample_image):
    """Test image preprocessing."""
    processor = DocumentProcessor()
    processed = processor.preprocess_image(sample_image)
    
    assert processed is not None
    assert processed.shape == sample_image.shape
    assert processed.dtype == np.uint8

def test_contour_detector_initialization():
    """Test ContourDetector initialization."""
    detector = ContourDetector()
    assert detector.min_area == 1000
    assert detector.max_area is None

def test_contour_detector_find_contours(sample_image):
    """Test contour detection."""
    detector = ContourDetector()
    
    # Create a new test image with clear contours
    test_image = np.zeros((300, 500), dtype=np.uint8)
    cv2.rectangle(test_image, (100, 100), (200, 200), 255, -1)  # Filled rectangle
    
    edges = detector.detect_edges(test_image)
    contours = detector.find_contours(edges)
    
    assert len(contours) > 0
    assert all(isinstance(c, np.ndarray) for c in contours)

def test_data_extractor_patterns():
    """Test data extraction patterns."""
    extractor = DataExtractor()
    test_text = """
    Document ID: DOC-123
    Date: 01/15/2025
    Email: test@example.com
    Phone: +1-234-567-8900
    Amount: $1,234.56
    Measurement: 123.45 mm
    """
    
    result = extractor.process_text(test_text)
    
    assert len(result['document_ids']) > 0
    assert len(result['dates']) > 0
    assert len(result['emails']) > 0
    assert len(result['phone_numbers']) > 0
    assert len(result['amounts']) > 0
    assert len(result['measurements']) > 0

def test_data_extractor_empty_text():
    """Test data extraction with empty text."""
    extractor = DataExtractor()
    result = extractor.process_text("")
    
    assert isinstance(result, dict)
    assert all(isinstance(v, list) for v in result.values() if isinstance(v, list))
    assert all(len(v) == 0 for v in result.values() if isinstance(v, list))

def test_document_processor_invalid_file():
    """Test document processor with invalid file."""
    processor = DocumentProcessor()
    with pytest.raises(FileNotFoundError):
        processor.process("nonexistent_file.png")

def test_contour_detector_invalid_image():
    """Test contour detector with invalid image."""
    detector = ContourDetector()
    with pytest.raises(FileNotFoundError):
        detector.process_image("nonexistent_file.png")

if __name__ == '__main__':
    pytest.main(['-v'])