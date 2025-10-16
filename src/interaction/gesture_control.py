"""Gesture control module for document interaction."""
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Any, Tuple, List
import logging

class GestureController:
    """Controls document viewing and processing using hand gestures."""
    
    def __init__(self):
        """Initialize the gesture controller."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.logger = self._setup_logger()
        
        # Gesture commands mapping
        self.commands = {
            "Open Palm": "next_page",
            "Closed Fist": "previous_page",
            "Two Fingers": "zoom_in",
            "Three Fingers": "zoom_out",
            "Four Fingers": "rotate_right",
            "One Finger": "pan_mode"
        }
        
        # State variables
        self.is_panning = False
        self.pan_start_pos = None
        self.current_zoom = 1.0
        self.current_rotation = 0
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('GestureController')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def count_fingers(self, hand_landmarks) -> int:
        """
        Count number of fingers held up.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            int: Number of fingers detected
        """
        finger_tips = [8, 12, 16, 20]  # Index for finger tips (except thumb)
        thumb_tip = 4
        count = 0
        
        # Check thumb
        if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x:
            count += 1
        
        # Check other fingers
        for tip in finger_tips:
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                count += 1
        
        return count
    
    def detect_gesture(self, hand_landmarks) -> str:
        """
        Detect basic hand gestures.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            str: Detected gesture name
        """
        fingers_up = self.count_fingers(hand_landmarks)
        
        if fingers_up == 0:
            return "Closed Fist"
        elif fingers_up == 5:
            return "Open Palm"
        else:
            return f"{fingers_up} Fingers"
    
    def get_hand_center(self, hand_landmarks) -> Tuple[float, float]:
        """
        Calculate the center point of the hand.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            
        Returns:
            tuple: (x, y) coordinates of hand center
        """
        x_coords = [lm.x for lm in hand_landmarks.landmark]
        y_coords = [lm.y for lm in hand_landmarks.landmark]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return (center_x, center_y)
    
    def process_frame(self, frame: np.ndarray) -> Tuple[Dict[str, Any], np.ndarray]:
        """
        Process a video frame and detect gestures.
        
        Args:
            frame (np.ndarray): Input video frame
            
        Returns:
            tuple: (Command dict, Annotated frame)
        """
        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        command = {"name": None, "params": {}}
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Detect gesture
                gesture = self.detect_gesture(hand_landmarks)
                
                # Get hand center for additional parameters
                hand_center = self.get_hand_center(hand_landmarks)
                
                # Map gesture to command
                if gesture in self.commands:
                    command["name"] = self.commands[gesture]
                    command["params"] = {
                        "position": hand_center,
                        "gesture": gesture
                    }
                
                # Display gesture
                cv2.putText(
                    frame,
                    f"Gesture: {gesture}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                
                if command["name"]:
                    cv2.putText(
                        frame,
                        f"Command: {command['name']}",
                        (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )
        
        return command, frame
    
    def handle_gesture_command(self, command: Dict[str, Any], document_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle gesture commands and update document state.
        
        Args:
            command (dict): Gesture command
            document_state (dict): Current document state
            
        Returns:
            dict: Updated document state
        """
        if not command["name"]:
            return document_state
        
        new_state = document_state.copy()
        
        try:
            if command["name"] == "next_page":
                new_state["page"] = min(
                    new_state["page"] + 1,
                    new_state["total_pages"] - 1
                )
                
            elif command["name"] == "previous_page":
                new_state["page"] = max(0, new_state["page"] - 1)
                
            elif command["name"] == "zoom_in":
                new_state["zoom"] = min(new_state["zoom"] * 1.1, 3.0)
                
            elif command["name"] == "zoom_out":
                new_state["zoom"] = max(new_state["zoom"] / 1.1, 0.5)
                
            elif command["name"] == "rotate_right":
                new_state["rotation"] = (new_state["rotation"] + 90) % 360
                
            elif command["name"] == "pan_mode":
                if not self.is_panning:
                    self.is_panning = True
                    self.pan_start_pos = command["params"]["position"]
                else:
                    self.is_panning = False
                    current_pos = command["params"]["position"]
                    dx = current_pos[0] - self.pan_start_pos[0]
                    dy = current_pos[1] - self.pan_start_pos[1]
                    new_state["pan_x"] += dx * 100
                    new_state["pan_y"] += dy * 100
            
            self.logger.info(f"Executed command: {command['name']}")
            
        except Exception as e:
            self.logger.error(f"Error handling gesture command: {str(e)}")
        
        return new_state
    
    def close(self):
        """Release resources."""
        self.hands.close()