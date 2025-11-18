import pandas as pd
import os
from datetime import datetime

def view_attendance():
    """Lihat data kehadiran"""
    attendance_file = "attendance.csv"
    
    if not os.path.exists(attendance_file):
        print("File attendance belum ada. Belum ada yang absen.")
        return
    
    df = pd.read_csv(attendance_file)
    
    if df.empty:
        print("Belum ada data kehadiran.")
        return
    
    print("\n=== DATA KEHADIRAN ===")
    print(df.to_string(index=False))
    
    # Statistik kehadiran hari ini
    today = datetime.now().strftime("%Y-%m-%d")
    today_attendance = df[df['Date'] == today]
    
    print(f"\n=== KEHADIRAN HARI INI ({today}) ===")
    if not today_attendance.empty:
        print(today_attendance[['Name', 'Time']].to_string(index=False))
        print(f"\nTotal hadir hari ini: {len(today_attendance)} orang")
    else:
        print("Belum ada yang absen hari ini.")

if __name__ == "__main__":
    view_attendance()