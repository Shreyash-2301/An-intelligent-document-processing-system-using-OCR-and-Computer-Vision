import cv2
import numpy as np
import logging
from pathlib import Path

class ContourDetector:
    """A class to handle contour detection and ROI extraction from documents."""
    
    def __init__(self, min_area=1000, max_area=None):
        """
        Initialize the ContourDetector.
        
        Args:
            min_area (int): Minimum contour area to consider
            max_area (int, optional): Maximum contour area to consider
        """
        self.min_area = min_area
        self.max_area = max_area
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Set up logging configuration."""
        logger = logging.getLogger('ContourDetector')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def detect_edges(self, image):
        """
        Detect edges in the image using Canny edge detection.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Edge detected image
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detect edges
            edges = cv2.Canny(blurred, 50, 150)
            
            return edges
            
        except Exception as e:
            self.logger.error(f"Error in edge detection: {str(e)}")
            raise
    
    def find_contours(self, image):
        """
        Find and filter contours in the image.
        
        Args:
            image (np.ndarray): Edge detected image
            
        Returns:
            list: List of filtered contours
        """
        try:
            # Ensure image is binary
            _, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filter contours by area
            filtered_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.min_area:
                    if self.max_area is None or area < self.max_area:
                        filtered_contours.append(contour)
            
            return filtered_contours
            
        except Exception as e:
            self.logger.error(f"Error finding contours: {str(e)}")
            raise
    
    def extract_roi(self, image, contour):
        """
        Extract region of interest (ROI) from the image using contour.
        
        Args:
            image (np.ndarray): Original image
            contour (np.ndarray): Contour defining the ROI
            
        Returns:
            np.ndarray: Extracted ROI
        """
        try:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Extract ROI
            roi = image[y:y+h, x:x+w]
            
            return roi, (x, y, w, h)
            
        except Exception as e:
            self.logger.error(f"Error extracting ROI: {str(e)}")
            raise
    
    def process_image(self, image_path, output_dir=None, visualize=False):
        """
        Process an image to detect and extract ROIs.
        
        Args:
            image_path (str): Path to the image file
            output_dir (str, optional): Directory to save extracted ROIs
            visualize (bool): Whether to visualize the results
            
        Returns:
            list: List of extracted ROIs and their coordinates
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
            
            # Detect edges
            edges = self.detect_edges(image)
            
            # Find contours
            contours = self.find_contours(edges)
            
            # Extract ROIs
            results = []
            for i, contour in enumerate(contours):
                roi, coords = self.extract_roi(image, contour)
                results.append((roi, coords))
                
                # Save ROI if output directory is specified
                if output_dir:
                    output_path = Path(output_dir) / f"roi_{i}.png"
                    cv2.imwrite(str(output_path), roi)
            
            # Visualize results if requested
            if visualize:
                vis_image = image.copy()
                cv2.drawContours(vis_image, contours, -1, (0, 255, 0), 2)
                cv2.imshow('Detected Contours', vis_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            
            self.logger.info(f"Found {len(results)} regions of interest")
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            raise