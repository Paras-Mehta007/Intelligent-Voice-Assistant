# Intelligent Video Surveillance System

## Overview
The **Intelligent Video Surveillance System** is an AI-powered security and monitoring system that integrates **voice commands, a graphical user interface (GUI), face recognition, and gesture control** for real-time surveillance. This system enhances security by allowing users to interact through multiple input methods, ensuring a seamless and efficient monitoring experience.

## Features
### Phase 1: Basic Voice Assistant
- Implements **speech recognition** using the `SpeechRecognition` library.
- Uses **Google Text-to-Speech (gTTS)** for voice output.
- Supports **basic voice commands** for system interactions.

### Phase 2: GUI Development
- Built with **Tkinter** or **PyQt** for a user-friendly interface.
- Includes **buttons, labels, and controls** for managing the surveillance system.
- Integrates voice assistant controls into the GUI for improved usability.

### Phase 3: Face Recognition System
- Captures **video feed** using OpenCV.
- Implements **face detection and recognition**.
- Maintains a **database of authorized and unauthorized faces** for security enforcement.

### Phase 4: Gesture Control Integration
- Uses **OpenCV** and **MediaPipe** for **hand tracking** and **gesture recognition**.
- Defines **specific gestures** for actions like **starting/stopping monitoring, switching cameras**, etc.
- Integrates gesture controls with the **GUI and voice assistant** for a unified control system.

### Phase 5: System Integration and Testing
- Combines **voice assistant, GUI, face recognition, and gesture control** into a **cohesive system**.
- Optimizes for **real-time performance and responsiveness**.
- Conducts **extensive testing** to improve accuracy and speed.

### Phase 6: Final Touches and Presentation
- Enhances the **user interface (UI) and user experience (UX)**.
- Prepares **demo and documentation** for the final presentation.
- Adds **extra features and improvements** based on testing feedback.

## Tech Stack
- **Programming Language:** Python
- **Libraries & Frameworks:**
  - `SpeechRecognition` - for voice input
  - `gTTS` - for text-to-speech conversion
  - `Tkinter` / `PyQt` - for GUI development
  - `OpenCV` - for video processing and face recognition
  - `MediaPipe` - for gesture recognition

## Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/intelligent-video-surveillance.git
   cd intelligent-video-surveillance
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage
- **Voice Commands:** Activate and control the surveillance system via speech.
- **GUI Controls:** Use buttons and toggles for manual control.
- **Face Recognition:** Detect and identify authorized/unrecognized individuals.
- **Gesture Control:** Perform system actions with predefined hand gestures.

## Future Enhancements
- Implement **real-time alerts and notifications**.
- Add **cloud storage and remote access**.
- Enhance **AI-based anomaly detection**.

## Contributors
- [Paras Mehta](https://github.com/Paras-Mehta007)
- [Himadri Mehra]
- [Kritika Tewari]
- [Divyanshu Singh Parihar]

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
Special thanks to all contributors and the open-source community for providing useful resources and libraries.

