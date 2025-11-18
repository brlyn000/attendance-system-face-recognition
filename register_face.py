import cv2
import os

def register_new_face():
    """Program untuk mendaftarkan wajah baru"""
    name = input("Masukkan nama karyawan: ")
    
    # Buat folder faces jika belum ada
    faces_dir = "faces"
    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)
    
    # Inisialisasi webcam
    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():
        print("Error: Tidak dapat mengakses webcam")
        return
    
    print(f"Tekan SPACE untuk mengambil foto {name}, atau ESC untuk batal")
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
            
        cv2.imshow('Register Face - Tekan SPACE untuk foto', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Space untuk ambil foto
            filename = os.path.join(faces_dir, f"{name}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Foto {name} berhasil disimpan sebagai {filename}")
            break
        elif key == 27:  # ESC untuk batal
            print("Pendaftaran dibatalkan")
            break
    
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    register_new_face()