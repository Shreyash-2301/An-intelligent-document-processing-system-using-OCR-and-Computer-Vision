import pytest
import cv2
import numpy as np
from src.vision.image_enhancement import (
    enhance_image,
    deskew_image,
    remove_background,
    auto_crop
)

@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    # Create a white image
    img = np.ones((300, 500), dtype=np.uint8) * 255
    
    # Add some text at an angle
    font = cv2.FONT_HERSHEY_SIMPLEX
    center = (200, 150)
    M = cv2.getRotationMatrix2D(center, 15, 1.0)  # 15-degree rotation
    img = cv2.warpAffine(img, M, (500, 300))
    cv2.putText(img, 'Test Document', (50, 150), font, 1, (0, 0, 0), 2)
    
    return img

def test_enhance_image(sample_image):
    """Test image enhancement."""
    enhanced = enhance_image(sample_image)
    
    assert enhanced is not None
    assert enhanced.shape == sample_image.shape
    assert enhanced.dtype == np.uint8
    
    # Check if contrast is improved
    assert cv2.meanStdDev(enhanced)[1] >= cv2.meanStdDev(sample_image)[1]

def test_deskew_image(sample_image):
    """Test image deskewing."""
    deskewed = deskew_image(sample_image)
    
    assert deskewed is not None
    assert deskewed.shape == sample_image.shape
    assert deskewed.dtype == sample_image.dtype

def test_remove_background(sample_image):
    """Test background removal."""
    cleaned = remove_background(sample_image)
    
    assert cleaned is not None
    assert cleaned.shape == sample_image.shape
    assert cleaned.dtype == np.uint8
    
    # Check if result is binary
    unique_values = np.unique(cleaned)
    assert len(unique_values) <= 2
    assert 0 in unique_values
    assert 255 in unique_values

def test_auto_crop(sample_image):
    """Test automatic cropping."""
    cropped, (x, y, w, h) = auto_crop(sample_image)
    
    assert cropped is not None
    assert isinstance(x, int)
    assert isinstance(y, int)
    assert isinstance(w, int)
    assert isinstance(h, int)
    assert cropped.shape[0] <= sample_image.shape[0]
    assert cropped.shape[1] <= sample_image.shape[1]