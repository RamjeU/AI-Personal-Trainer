import cv2
import mediapipe as mp
import numpy as np
# Note: Importing the new functions from trainer_utils
from trainer_utils import calculate_angle, draw_dual_info_box, draw_hud_bar

# --- CONFIGURATION ---
# Colors (BGR)
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_BLUE = (255, 0, 0)
# Thresholds
VISIBILITY_THRESHOLD = 0.65
SHOULDER_WIDTH_MIN = 0.1
SHOULDER_WIDTH_MAX = 0.8

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# --- STATE VARIABLES (DUAL ARMS) ---
left_counter = 0
left_stage = None
right_counter = 0
right_stage = None

app_state = "SETUP" # SETUP -> WORKOUT

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Image Pre-processing
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        height, width, _ = image.shape

        # Logic Flow
        try:
            landmarks = results.pose_landmarks.landmark
            
            # --- PHASE 1: CHECK POSITION (SETUP) ---
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
            shoulder_width = abs(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x - 
                                 landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x)
            
            hips_visible = (left_hip.visibility > VISIBILITY_THRESHOLD and 
                            right_hip.visibility > VISIBILITY_THRESHOLD)

            feedback_text = "Looking for user..."
            feedback_color = COLOR_RED

            if not hips_visible:
                feedback_text = "Step Back (Show Hips)"
                app_state = "SETUP"
            elif shoulder_width < SHOULDER_WIDTH_MIN:
                feedback_text = "Too Far! Step Closer"
                app_state = "SETUP"
            elif shoulder_width > SHOULDER_WIDTH_MAX:
                feedback_text = "Too Close! Step Back"
                app_state = "SETUP"
            else:
                feedback_text = "GO! Workout Active."
                feedback_color = COLOR_GREEN
                app_state = "WORKOUT"

            # Display Setup Instructions (BIGGER TEXT)
            if app_state == "SETUP":
                 # Increased font scale from 1 to 1.3 for better visibility
                text_size = cv2.getTextSize(feedback_text, cv2.FONT_HERSHEY_SIMPLEX, 1.3, 3)[0]
                text_x = (width - text_size[0]) // 2
                text_y = (height + text_size[1]) // 2
                
                cv2.rectangle(image, (text_x - 10, text_y - 50), (text_x + text_size[0] + 10, text_y + 15), (0,0,0), -1)
                cv2.putText(image, feedback_text, (text_x, text_y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, feedback_color, 3, cv2.LINE_AA)

            # --- PHASE 2: THE WORKOUT (DUAL ARM TRACKING) ---
            
            if app_state == "WORKOUT":
                # --- LEFT ARM LOGIC ---
                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                
                l_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
                
                if l_angle > 160: left_stage = "down"
                if l_angle < 30 and left_stage == 'down':
                    left_stage = "up"
                    left_counter += 1

                # --- RIGHT ARM LOGIC ---
                r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                r_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                r_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                
                r_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
                
                if r_angle > 160: right_stage = "down"
                if r_angle < 30 and right_stage == 'down':
                    right_stage = "up"
                    right_counter += 1
                
                # --- VISUALIZATION ---
                
                # 1. Draw Dual Info Box (Top Left)
                draw_dual_info_box(image, left_counter, right_counter)

                # 2. Helper Text (BIGGER)
                # Increased font scale to 1.0 and thickness to 2
                cv2.putText(image, "Stand angled 45 deg for best results", (width - 350, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_YELLOW, 2, cv2.LINE_AA)
                
                # --- BOTTOM HUD IMPLEMENTATION ---
                
                # Calculate Percentages for bars (160deg=0%, 30deg=100%)
                l_per = np.interp(l_angle, (30, 160), (100, 0))
                r_per = np.interp(r_angle, (30, 160), (100, 0))
                # Average activity for the middle bar
                both_per = (l_per + r_per) / 2

                # HUD Geometry setup (Bottom center)
                hud_height = 30
                hud_y_pos = height - 50 # 50 pixels from bottom
                bar_width = 150
                gap = 20
                
                # Calculate starting X coordinate to center the three bars
                total_hud_width = (bar_width * 3) + (gap * 2)
                start_x = (width - total_hud_width) // 2

                # Draw Left Bar
                draw_hud_bar(image, start_x, hud_y_pos, bar_width, hud_height, l_per, COLOR_BLUE, "Left Arm")
                
                # Draw Middle Bar (Both/Avg)
                mid_x = start_x + bar_width + gap
                draw_hud_bar(image, mid_x, hud_y_pos, bar_width, hud_height, both_per, COLOR_GREEN, "Avg Activity")
                
                # Draw Right Bar
                right_x = mid_x + bar_width + gap
                draw_hud_bar(image, right_x, hud_y_pos, bar_width, hud_height, r_per, COLOR_BLUE, "Right Arm")


        except Exception as e:
            # Basic error handling if landmarks fail completely
            pass

        # Render Skeleton
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))
        
        cv2.imshow('AI Personal Trainer - Dual Mode', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()