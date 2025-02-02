import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import customtkinter as ctk
from threading import Thread
import time

class HandGestureController:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # System control flags
        self.is_running = True
        self.enable_controls = False
        self.current_gesture = "None"
        self.finger_count = 0
        
        # Gesture cooldown
        self.last_action_time = time.time()
        self.cooldown = 1.0  # seconds
        
        # Create GUI
        self.create_gui()
        
    def create_gui(self):
        self.root = ctk.CTk()
        self.root.title("Hand Gesture Control System")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="Hand Gesture Control System", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=10)
        
        # Camera frame
        self.camera_frame = ctk.CTkFrame(main_frame)
        self.camera_frame.pack(pady=10)
        
        # Status frame
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(pady=10, fill="x", padx=20)
        
        # Status labels
        self.gesture_label = ctk.CTkLabel(status_frame, text="Current Gesture: None")
        self.gesture_label.pack(pady=5)
        
        self.fingers_label = ctk.CTkLabel(status_frame, text="Fingers Count: 0")
        self.fingers_label.pack(pady=5)
        
        # Control buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        
        self.control_btn = ctk.CTkSwitch(button_frame, text="Enable Controls", 
                                      command=self.toggle_controls)
        self.control_btn.pack(side="left", padx=10)
        
        # Instructions
        self.create_instructions(main_frame)
        
    def create_instructions(self, parent):
        instructions = """
        Gesture Controls:
        • ✌️ Peace Sign - Volume Up
        • 👆 One Finger - Volume Down
        • ✋ Open Palm - Play/Pause Media
        • 👊 Fist - Mute
        • 🤟 Rock Sign - Next Track
        • 👍 Thumbs Up - Previous Track
        • ✋ Five Fingers + Move - Mouse Control
        • 🤘 Exit Gesture - Close Program
        """
        
        inst_label = ctk.CTkLabel(parent, text=instructions, 
                                justify="left", 
                                font=ctk.CTkFont(size=12))
        inst_label.pack(pady=10)
        
    def toggle_controls(self):
        self.enable_controls = self.control_btn.get()
        
    def count_fingers(self, hand_landmarks):
        finger_tips = [8, 12, 16, 20]  # Index of finger tips
        thumb_tip = 4
        count = 0
        
        # Check thumb
        if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x:
            count += 1
            
        # Check fingers
        for tip in finger_tips:
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                count += 1
                
        return count
        
    def detect_gesture(self, hand_landmarks):
        fingers = self.count_fingers(hand_landmarks)
        self.finger_count = fingers
        
        # Update GUI
        self.fingers_label.configure(text=f"Fingers Count: {fingers}")
        
        # Basic gesture detection
        if fingers == 2:
            return "Peace"
        elif fingers == 1:
            return "One Finger"
        elif fingers == 5:
            return "Open Palm"
        elif fingers == 0:
            return "Fist"
        elif fingers == 3:
            return "Rock Sign"
        
        return "None"
        
    def perform_action(self, gesture):
        if not self.enable_controls:
            return
            
        current_time = time.time()
        if current_time - self.last_action_time < self.cooldown:
            return
            
        self.last_action_time = current_time
        
        if gesture == "Peace":
            pyautogui.press('volumeup')
        elif gesture == "One Finger":
            pyautogui.press('volumedown')
        elif gesture == "Open Palm":
            pyautogui.press('playpause')
        elif gesture == "Fist":
            pyautogui.press('volumemute')
        elif gesture == "Rock Sign":
            pyautogui.press('nexttrack')
        
    def start_camera(self):
        cap = cv2.VideoCapture(0)
        
        while self.is_running:
            success, image = cap.read()
            if not success:
                print("Failed to capture image")
                break
                
            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            results = self.hands.process(image_rgb)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Detect gesture
                    gesture = self.detect_gesture(hand_landmarks)
                    if gesture != self.current_gesture:
                        self.current_gesture = gesture
                        self.gesture_label.configure(text=f"Current Gesture: {gesture}")
                        self.perform_action(gesture)
            
            # Convert to RGB for display
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Display the image
            cv2.imshow('Hand Gesture Recognition', image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.is_running = False
                
        cap.release()
        cv2.destroyAllWindows()
        self.root.quit()
        
    def run(self):
        # Start camera in a separate thread
        camera_thread = Thread(target=self.start_camera)
        camera_thread.start()
        
        # Run GUI
        self.root.mainloop()
        
        # Cleanup
        self.is_running = False
        camera_thread.join()

if __name__ == "__main__":
    controller = HandGestureController()
    controller.run() 