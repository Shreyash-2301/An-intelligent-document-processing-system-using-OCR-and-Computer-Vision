"""Image enhancement utilities for improving OCR accuracy."""
import cv2
import numpy as np
from typing import Tuple

def enhance_image(image: np.ndarray) -> np.ndarray:
    """
    Enhance image quality for better OCR results.
    
    Args:
        image (np.ndarray): Input image
        
    Returns:
        np.ndarray: Enhanced image
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced)
    
    # Sharpen the image
    kernel = np.array([[-1,-1,-1],
                      [-1, 9,-1],
                      [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    return sharpened

def deskew_image(image: np.ndarray) -> np.ndarray:
    """
    Deskew the image by detecting and correcting text orientation.
    
    Args:
        image (np.ndarray): Input image
        
    Returns:
        np.ndarray: Deskewed image
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Calculate skew angle
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords.astype(np.float32))[-1]
    
    if angle < -45:
        angle = 90 + angle
    
    # Rotate the image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                            flags=cv2.INTER_CUBIC,
                            borderMode=cv2.BORDER_REPLICATE)
    
    return rotated

def remove_background(image: np.ndarray) -> np.ndarray:
    """
    Remove background noise and enhance text.
    
    Args:
        image (np.ndarray): Input image
        
    Returns:
        np.ndarray: Image with removed background
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Apply morphological operations
    kernel = np.ones((3,3), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    return cleaned

def auto_crop(image: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """
    Automatically crop the image to content area.
    
    Args:
        image (np.ndarray): Input image
        
    Returns:
        tuple: (Cropped image, (x, y, w, h) crop coordinates)
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find bounding box of all contours
    x, y, w, h = 0, 0, image.shape[1], image.shape[0]
    if contours:
        x_coords = []
        y_coords = []
        for contour in contours:
            x_temp, y_temp, w_temp, h_temp = cv2.boundingRect(contour)
            x_coords.extend([x_temp, x_temp + w_temp])
            y_coords.extend([y_temp, y_temp + h_temp])
        
        x = min(x_coords)
        y = min(y_coords)
        w = max(x_coords) - x
        h = max(y_coords) - y
    
    # Add padding
    padding = 10
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(image.shape[1] - x, w + 2 * padding)
    h = min(image.shape[0] - y, h + 2 * padding)
    
    # Crop image
    cropped = image[y:y+h, x:x+w]
    
    return cropped, (x, y, w, h)