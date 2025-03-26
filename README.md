# Intelligent Voice Assistant

## Overview
The **Intelligent Voice Assistant** is an AI-powered system that integrates **voice commands, a graphical user interface (GUI), and gesture control** for seamless interaction. This system enhances user experience by allowing multiple input methods for better accessibility and efficiency.

## Features
### Phase 1: Basic Voice Assistant
- Implements **speech recognition** using the `SpeechRecognition` library.
- Uses **Google Text-to-Speech (gTTS)** for voice output.
- Supports **basic voice commands** for system interactions.

### Phase 2: GUI Development
- Built with **Tkinter** or **PyQt** for a user-friendly interface.
- Includes **buttons, labels, and controls** for managing the assistant.
- Integrates voice assistant controls into the GUI for improved usability.

### Phase 3: Face Recognition System
- Captures **video feed** using OpenCV.
- Implements **face detection and recognition**.
- Maintains a **database of authorized and unauthorized faces** for security enforcement.

### Phase 4: Gesture Control Integration
- Uses **OpenCV** and **MediaPipe** for **hand tracking** and **gesture recognition**.
- Defines **specific gestures** for actions like **activating the assistant, controlling applications, etc.**.
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
   git clone https://github.com/your-username/intelligent-voice-assistant.git
   cd intelligent-voice-assistant
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
- **Voice Commands:** Activate and control the assistant via speech.
- **GUI Controls:** Use buttons and toggles for manual control.
- **Face Recognition:** Detect and identify authorized/unrecognized individuals.
- **Gesture Control:** Perform system actions with predefined hand gestures.

## Future Enhancements
- Implement **real-time alerts and notifications**.
- Add **cloud storage and remote access**.
- Enhance **AI-based automation and integrations**.
  
## Contributors
- [Paras Mehta](https://github.com/Paras-Mehta007)
- [Himadri Mehra]
- [Kritika Tewari]
- [Divyanshu Singh Parihar]

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
Special thanks to all contributors and the open-source community for providing useful resources and libraries.

