import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os

class AttendanceSystem:
    def __init__(self):
        self.known_faces = {}  # Dictionary: name -> list of face encodings
        self.attendance_file = "attendance.csv"
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.load_known_faces()
        
    def extract_face_features(self, image):
        """Extract simple face features using histogram"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Resize to standard size
        face = cv2.resize(gray, (100, 100))
        
        # Calculate histogram
        hist = cv2.calcHist([face], [0], None, [256], [0, 256])
        
        # Normalize histogram
        hist = cv2.normalize(hist, hist).flatten()
        
        return hist
        
    def load_known_faces(self):
        """Load gambar wajah yang sudah terdaftar dari folder 'faces'"""
        faces_dir = "faces"
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
            print(f"Folder '{faces_dir}' dibuat. Silakan tambahkan foto wajah karyawan.")
            return
            
        for filename in os.listdir(faces_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                name = os.path.splitext(filename)[0]
                image_path = os.path.join(faces_dir, filename)
                
                image = cv2.imread(image_path)
                if image is not None:
                    # Detect face in the image
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    if len(faces) > 0:
                        # Take the largest face
                        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                        face_crop = image[y:y+h, x:x+w]
                        
                        # Extract features
                        features = self.extract_face_features(face_crop)
                        
                        if name not in self.known_faces:
                            self.known_faces[name] = []
                        self.known_faces[name].append(features)
                        
                        print(f"Wajah {name} berhasil dimuat")
                    else:
                        print(f"Tidak ada wajah terdeteksi di {filename}")
    
    def compare_faces(self, features1, features2):
        """Compare two face feature vectors"""
        # Use correlation coefficient
        correlation = np.corrcoef(features1, features2)[0, 1]
        return correlation if not np.isnan(correlation) else 0
    
    def recognize_face(self, face_image):
        """Recognize face from image"""
        features = self.extract_face_features(face_image)
        
        best_match = None
        best_score = 0.7  # Minimum threshold
        
        for name, known_features_list in self.known_faces.items():
            scores = []
            for known_features in known_features_list:
                score = self.compare_faces(features, known_features)
                scores.append(score)
            
            # Take average score for this person
            avg_score = np.mean(scores) if scores else 0
            
            if avg_score > best_score:
                best_score = avg_score
                best_match = name
        
        return best_match, best_score
    
    def mark_attendance(self, name):
        """Catat kehadiran ke file CSV"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        if os.path.exists(self.attendance_file):
            df = pd.read_csv(self.attendance_file)
        else:
            df = pd.DataFrame(columns=['Name', 'Date', 'Time'])
        
        today_attendance = df[(df['Name'] == name) & (df['Date'] == date_str)]
        
        if today_attendance.empty:
            new_record = pd.DataFrame({
                'Name': [name],
                'Date': [date_str], 
                'Time': [time_str]
            })
            df = pd.concat([df, new_record], ignore_index=True)
            df.to_csv(self.attendance_file, index=False)
            print(f"✅ Kehadiran {name} tercatat pada {date_str} {time_str}")
            return True
        else:
            print(f"⚠️ {name} sudah absen hari ini")
            return False
    
    def run_attendance(self):
        """Jalankan sistem attendance dengan webcam"""
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            print("Error: Tidak dapat mengakses webcam")
            return
            
        print("🎥 Sistem attendance dimulai.")
        print("📋 Tekan SPACE untuk scan wajah, 'q' untuk keluar")
        
        last_recognition_time = 0
        recognition_cooldown = 3  # seconds
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            current_time = datetime.now().timestamp()
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Auto recognition with cooldown
                if current_time - last_recognition_time > recognition_cooldown:
                    face_crop = frame[y:y+h, x:x+w]
                    
                    if face_crop.size > 0:
                        name, confidence = self.recognize_face(face_crop)
                        
                        if name:
                            cv2.putText(frame, f"{name} ({confidence:.2f})", (x, y-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            self.mark_attendance(name)
                            last_recognition_time = current_time
                        else:
                            cv2.putText(frame, "Unknown", (x, y-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "Face Detected", (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
            # Show instructions
            cv2.putText(frame, "SPACE: Manual scan | Q: Quit", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Face Recognition Attendance', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' ') and len(faces) > 0:
                # Manual recognition
                x, y, w, h = faces[0]
                face_crop = frame[y:y+h, x:x+w]
                
                if face_crop.size > 0:
                    name, confidence = self.recognize_face(face_crop)
                    
                    if name:
                        print(f"🔍 Manual scan: {name} (confidence: {confidence:.2f})")
                        self.mark_attendance(name)
                    else:
                        print("❌ Wajah tidak dikenali")
        
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    attendance_system = AttendanceSystem()
    attendance_system.run_attendance()