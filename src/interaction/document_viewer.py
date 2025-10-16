"""Interactive document viewer with gesture control."""
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

from src.interaction.gesture_control import GestureController
from src.ocr.processor import DocumentProcessor
from src.vision.image_enhancement import enhance_image

class GestureControlledViewer:
    """Interactive document viewer with gesture control support."""
    
    def __init__(self, document_path: str):
        """
        Initialize the viewer.
        
        Args:
            document_path (str): Path to the document to view
        """
        self.document_path = Path(document_path)
        self.gesture_controller = GestureController()
        self.doc_processor = DocumentProcessor()
        
        # Initialize document state
        self.state = {
            "page": 0,
            "total_pages": 1,
            "zoom": 1.0,
            "rotation": 0,
            "pan_x": 0,
            "pan_y": 0,
            "processed": False
        }
        
        # Load document
        self.load_document()
    
    def load_document(self):
        """Load and preprocess the document."""
        try:
            # Load image
            self.original_image = cv2.imread(str(self.document_path))
            if self.original_image is None:
                raise ValueError(f"Failed to load image: {self.document_path}")
            
            # Enhance image
            self.enhanced_image = enhance_image(self.original_image)
            
            # Initialize display image
            self.display_image = self.enhanced_image.copy()
            
        except Exception as e:
            print(f"Error loading document: {str(e)}")
            raise
    
    def update_display(self) -> np.ndarray:
        """
        Update the display image based on current state.
        
        Returns:
            np.ndarray: Updated display image
        """
        # Start with enhanced image
        img = self.enhanced_image.copy()
        
        # Apply rotation
        if self.state["rotation"] != 0:
            center = (img.shape[1] // 2, img.shape[0] // 2)
            M = cv2.getRotationMatrix2D(center, self.state["rotation"], 1.0)
            img = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
        
        # Apply zoom
        if self.state["zoom"] != 1.0:
            width = int(img.shape[1] * self.state["zoom"])
            height = int(img.shape[0] * self.state["zoom"])
            img = cv2.resize(img, (width, height))
        
        # Apply pan
        if self.state["pan_x"] != 0 or self.state["pan_y"] != 0:
            M = np.float32([[1, 0, self.state["pan_x"]], [0, 1, self.state["pan_y"]]])
            img = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
        
        self.display_image = img
        return img
    
    def process_document(self):
        """Process document with OCR if not already processed."""
        if not self.state["processed"]:
            try:
                # Extract text
                text = self.doc_processor.process(self.document_path)
                
                # Draw OCR results
                img = self.display_image.copy()
                cv2.putText(
                    img,
                    "OCR Processing Complete",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                
                self.display_image = img
                self.state["processed"] = True
                
            except Exception as e:
                print(f"Error processing document: {str(e)}")
    
    def run(self):
        """Run the interactive viewer."""
        print("Gesture-Controlled Document Viewer")
        print("Gestures:")
        print("- Open Palm: Next page")
        print("- Closed Fist: Previous page")
        print("- Two Fingers: Zoom in")
        print("- Three Fingers: Zoom out")
        print("- Four Fingers: Rotate right")
        print("- One Finger: Pan mode")
        print("Press 'q' to quit")
        
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        
        try:
            while True:
                # Read frame from webcam
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process gestures
                command, annotated_frame = self.gesture_controller.process_frame(frame)
                
                # Handle gesture command
                self.state = self.gesture_controller.handle_gesture_command(
                    command, self.state
                )
                
                # Update document display
                doc_view = self.update_display()
                
                # Show both webcam feed and document
                cv2.imshow('Gesture Control', annotated_frame)
                cv2.imshow('Document View', doc_view)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        finally:
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            self.gesture_controller.close()