import numpy as np
import cv2

def calculate_angle(a, b, c):
    """
    Calculates the angle between three points (a, b, c).
    b is the vertex (the elbow).
    """
    a = np.array(a) # Shoulder
    b = np.array(b) # Elbow
    c = np.array(c) # Wrist
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def draw_dual_info_box(image, l_count, r_count):
    """
    Draws a UI box on the top left to display Left and Right reps.
    """
    # Create a rectangle background
    # Wider box to fit two numbers
    cv2.rectangle(image, (0, 0), (280, 80), (245, 117, 16), -1) 
    
    # Left Rep Data
    cv2.putText(image, 'L REPS', (15, 12), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, str(l_count), (10, 65), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Divider Line
    cv2.line(image, (140, 5), (140, 75), (255,255,255), 2)

    # Right Rep Data
    cv2.putText(image, 'R REPS', (155, 12), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, str(r_count), (150, 65), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

def draw_hud_bar(image, x, y, width, height, percentage, color, label):
    """
    Helper function to draw a horizontal progress bar with a label.
    """
    # 1. Draw Label/Title over the bar
    cv2.putText(image, label, (x, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    # 2. Draw the Bar Outline/Background
    cv2.rectangle(image, (x, y), (x + width, y + height), (50, 50, 50), -1) # Dark gray bg
    cv2.rectangle(image, (x, y), (x + width, y + height), color, 2) # Colored border

    # 3. Calculate Fill width based on percentage
    # Ensure percentage is clamped between 0 and 100
    safe_per = max(0, min(100, percentage))
    fill_width = int((safe_per / 100) * width)

    # 4. Draw the Bar Fill
    if fill_width > 0:
         cv2.rectangle(image, (x, y), (x + fill_width, y + height), color, -1)