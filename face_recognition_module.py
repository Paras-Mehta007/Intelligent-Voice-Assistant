import cv2
import numpy as np
import os
import pickle
import time
from datetime import datetime

class FaceRecognition:
    def __init__(self, data_dir="face_data"):
        """Initialize the face recognition system"""
        self.data_dir = data_dir
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Create directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            os.makedirs(os.path.join(data_dir, "users"))
        
        # Load existing face data if available
        self.face_data = {}
        self.load_face_data()
        
        # Try to load the recognizer model if it exists
        model_path = os.path.join(self.data_dir, "face_model.yml")
        if os.path.exists(model_path):
            try:
                self.recognizer.read(model_path)
                print("Face recognition model loaded successfully")
            except Exception as e:
                print(f"Error loading face model: {e}")

    def load_face_data(self):
        """Load face data from pickle file"""
        data_file = os.path.join(self.data_dir, "face_data.pkl")
        if os.path.exists(data_file):
            with open(data_file, 'rb') as f:
                self.face_data = pickle.load(f)
            print(f"Loaded face data for {len(self.face_data)} users")

    def save_face_data(self):
        """Save face data to pickle file"""
        data_file = os.path.join(self.data_dir, "face_data.pkl")
        with open(data_file, 'wb') as f:
            pickle.dump(self.face_data, f)

    def register_new_user(self, user_name, capture_count=30):
        """Register a new user by capturing face images"""
        user_id = len(self.face_data) + 1
        face_samples = []
        
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
                face_samples.append(face_sample)
                count += 1
                
            cv2.imshow('Registration', frame)
            cv2.waitKey(100)
            
            if count % 5 == 0:
                print(f"Captured {count}/{capture_count} images")
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Save user data
        self.face_data[user_id] = {
            'name': user_name,
            'registered_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Train recognizer
        labels = [user_id] * len(face_samples)
        self.recognizer.train(face_samples, np.array(labels))
        
        # Save model and data
        self.recognizer.save(os.path.join(self.data_dir, "face_model.yml"))
        self.save_face_data()
        
        return user_id

    def recognize_face(self, frame):
        """Recognize face in the given frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        results = []
        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))
            
            try:
                label, confidence = self.recognizer.predict(face)
                if confidence < 100:  # Lower confidence is better
                    name = self.face_data[label]['name']
                    results.append({
                        'name': name,
                        'confidence': confidence,
                        'bbox': (x, y, w, h)
                    })
            except Exception as e:
                print(f"Error during recognition: {e}")
        
        return results

    def start_recognition(self):
        """Start continuous face recognition"""
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            results = self.recognize_face(frame)
            
            for result in results:
                x, y, w, h = result['bbox']
                name = result['name']
                confidence = result['confidence']
                
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Put text
                text = f"{name} ({confidence:.2f}%)"
                cv2.putText(frame, text, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            
            cv2.imshow('Face Recognition', frame)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    # Create face recognition system
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
