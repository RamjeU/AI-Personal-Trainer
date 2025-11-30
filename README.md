# 🏋️ AI Dual-Arm Personal Trainer

An advanced computer vision application that acts as a real-time personal trainer. It uses MediaPipe and OpenCV to track dual-arm bicep curls, ensuring correct form, counting repetitions, and providing visual feedback via a dynamic HUD.

## 🚀 Features
* **Smart "Ready" State:** Uses pose calibration to ensure the user is at the correct distance and angle before starting the workout.
* **Dual-Arm Tracking:** Simultaneously tracks left and right arms with independent logic.
* **Visual HUD:** Real-time feedback including:
    * Rep counters for both arms.
    * Progress bars (0-100%) for flexion/extension.
    * "Average Activity" metric for balanced workouts.
* **Form Correction:** Detects if the user is facing the wrong way or is too close/far from the camera.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Computer Vision:** OpenCV (`cv2`)
* **Pose Estimation:** Google MediaPipe
* **Math:** NumPy (Trigonometric angle calculation & interpolation)

## 💻 How to Run

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/ai-personal-trainer.git](https://github.com/yourusername/ai-personal-trainer.git)
    cd ai-personal-trainer
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    python main.py
    ```

## 🧠 How it Works
The application calculates the angle $\theta$ between the shoulder, elbow, and wrist landmarks using the arctangent function:

$$ \theta = |\arctan2(y_C - y_B, x_C - x_B) - \arctan2(y_A - y_B, x_A - x_B)| $$

State machines monitor this angle to distinguish between "UP" (Flexion < 30°) and "DOWN" (Extension > 160°) states to prevent false positives.

## 📄 License
This project is licensed under the MIT License.
