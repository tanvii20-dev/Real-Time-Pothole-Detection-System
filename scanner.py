import cv2
from ultralytics import YOLO
import requests
import time

# --- CONFIGURATION ---
MODEL_PATH = "best.pt"  # Your trained YOLOv8 model
VIDEO_PATH = "pothole_video.mp4"  # Put your video file name here!
API_URL = "http://127.0.0.1:8000/report_hazard"

# Simulated Starting GPS in Pune
CURRENT_LAT = 18.5204 
CURRENT_LON = 73.8567

# Load AI
model = YOLO(MODEL_PATH)

def broadcast_to_v2v(lat, lon, conf):
    payload = {"lat": lat, "lon": lon, "severity": int(conf * 10)}
    try:
        requests.post(API_URL, json=payload, timeout=0.5)
        return True
    except:
        return False

# Open Video File
cap = cv2.VideoCapture(VIDEO_PATH)
frame_count = 0

print(f"Analyzing Video: {VIDEO_PATH}...")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("End of video or file not found.")
        break

    frame_count += 1
    
    # Optimize: Only scan every 5th frame to keep it smooth and "Google-scale"
    if frame_count % 5 == 0:
        results = model(frame, conf=0.5, verbose=False)
        
        for r in results:
            for box in r.boxes:
                # 1. Logic: If a pothole is found, update the Global Map
                # We move the GPS slightly forward to simulate the car driving
                CURRENT_LAT += 0.0001 
                
                conf = box.conf[0]
                status = broadcast_to_v2v(CURRENT_LAT, CURRENT_LON, conf)
                
                # 2. Visual Feedback for your Demo
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"POTHOLE {conf:.2f}", (x1, y1-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                
                if status:
                    cv2.putText(frame, "V2V SYNC ACTIVE", (20, 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Vehicle A - Edge AI Scanner", frame)
    
    # Press 'q' to stop early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()