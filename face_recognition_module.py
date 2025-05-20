import cv2
import numpy as np
import os
import pickle
from datetime import datetime

class FaceRecognition:
    def __init__(self, data_dir="face_data"):
        """Initialize the face recognition system"""
        self.data_dir = data_dir
        self.users_dir = os.path.join(data_dir, "users")
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        # Create directories if they don't exist
        os.makedirs(self.users_dir, exist_ok=True)

        self.face_data = {}
        self.load_face_data()

        model_path = os.path.join(self.data_dir, "face_model.yml")
        if os.path.exists(model_path):
            try:
                self.recognizer.read(model_path)
                print("Face recognition model loaded successfully")
            except Exception as e:
                print(f"Error loading face model: {e}")

    def load_face_data(self):
        """Load face metadata"""
        data_file = os.path.join(self.data_dir, "face_data.pkl")
        if os.path.exists(data_file):
            with open(data_file, 'rb') as f:
                self.face_data = pickle.load(f)
            print(f"Loaded face data for {len(self.face_data)} users")

    def save_face_data(self):
        """Save face metadata"""
        data_file = os.path.join(self.data_dir, "face_data.pkl")
        with open(data_file, 'wb') as f:
            pickle.dump(self.face_data, f)

    def register_new_user(self, user_name, capture_count=30):
        """Register a new user by capturing face images"""
        user_id = len(self.face_data) + 1
        # user_id = max(self.face_data.keys(), default=0) + 1
        user_dir = os.path.join(self.users_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)

        cap = cv2.VideoCapture(0)
        count = 0

        while count < capture_count:
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                face_sample = gray[y:y+h, x:x+w]
                face_sample = cv2.resize(face_sample, (200, 200))
                img_path = os.path.join(user_dir, f"{count}.png")
                cv2.imwrite(img_path, face_sample)
                count += 1

            cv2.imshow('Registration', frame)
            cv2.waitKey(100)

            if count % 5 == 0:
                print(f"Captured {count}/{capture_count} images")

        cap.release()
        cv2.destroyAllWindows()

        self.face_data[user_id] = {
            'name': user_name,
            'registered_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.save_face_data()
        self.train_recognizer()
        return user_id

    def train_recognizer(self):
        """Train recognizer with all user images"""
        face_samples = []
        labels = []

        for user_id, user_info in self.face_data.items():
            user_dir = os.path.join(self.users_dir, str(user_id))
            for img_name in os.listdir(user_dir):
                img_path = os.path.join(user_dir, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    face_samples.append(img)
                    labels.append(int(user_id))

        if face_samples:
            self.recognizer.train(face_samples, np.array(labels))
            self.recognizer.save(os.path.join(self.data_dir, "face_model.yml"))
            print("Model trained and saved with all users.")

    def recognize_face(self, frame,confidence_threshold=60):
        """Recognize face in the given frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        results = []
        MIN_CONFIDENCE = confidence_threshold  # Lower is better in OpenCV LBPH


        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))

            try:
                label, confidence = self.recognizer.predict(face)
                print(f"Predicted: {label}, Confidence: {confidence:.2f}")

                if confidence < MIN_CONFIDENCE and label in self.face_data:
                    name = self.face_data[label]['name']
                    results.append({
                        'name': name,
                        'confidence': confidence,
                        'bbox': (x, y, w, h),
                        'valid':True
                    })
                else:
                    results.append({
                        'name': "Unknown",
                        'confidence': confidence,
                        'bbox': (x, y, w, h),
                        'valid':False
                    })
            except Exception as e:
                print(f"Recognition error: {e}")

        
 
        return results

   
    def start_recognition(self):
        """Start continuous face recognition"""
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            results = self.recognize_face(frame)
            
            # First check if any faces were detected
            if not results:
                # No faces detected in frame
                cv2.putText(frame, "No face detected", (30, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            else:
                # Process each detected face
                for result in results:
                    x, y, w, h = result['bbox']
                    name = result['name']
                    confidence = result['confidence']
                    is_valid = result['valid']
                    
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    if is_valid:
                        text = f"{name} ({confidence:.2f})"
                        color = (0, 255, 0)  # Green
                        # 🚀 Launch assistant here ONLY
                        # start_voice_assistant()
                    else:
                        text = "Unknown. Please register."
                        color = (0, 0, 255)  # Red
                    
                    cv2.putText(frame, text, (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            cv2.imshow('Face Recognition', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

def main():
    face_system = FaceRecognition()

    while True:
        print("\nFace Recognition System")
        print("1. Register new user")
        print("2. Start face recognition")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            name = input("Enter user name: ")
            print("Starting user registration...")
            face_system.register_new_user(name)
            print("Registration complete!")

        elif choice == '2':
            print("Starting face recognition...")
            face_system.start_recognition()

        elif choice == '3':
            print("Exiting...")
            break

        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()

