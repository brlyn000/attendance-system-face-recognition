#!/bin/bash

# Script untuk menjalankan sistem attendance dengan virtual environment

echo "=== Face Recognition Attendance System ==="
echo "1. Daftarkan wajah karyawan"
echo "2. Jalankan sistem attendance"
echo "3. Lihat data kehadiran"
echo "4. Keluar"
echo

read -p "Pilih menu (1-4): " choice

case $choice in
    1)
        echo "Menjalankan pendaftaran wajah..."
        source venv/bin/activate && python register_face.py
        ;;
    2)
        echo "Menjalankan sistem attendance..."
        source venv/bin/activate && python face_recognition.py
        ;;
    3)
        echo "Menampilkan data kehadiran..."
        source venv/bin/activate && python view_attendance.py
        ;;
    4)
        echo "Keluar..."
        exit 0
        ;;
    *)
        echo "Pilihan tidak valid!"
        ;;
esac