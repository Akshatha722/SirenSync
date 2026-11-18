
import cv2
import requests
import time
from ultralytics import YOLO

# Load trained ambulance detection model
model = YOLO("models/ambulance_best.pt")

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera not available")
    exit()

print("SirenSync AI Camera Monitor Started")
print("Press Q to quit")

emergency_active = False
detected_frames = 0
missing_frames = 0
last_count_update = 0

while True:

    success, frame = camera.read()

    if not success:
        print("Unable to read camera")
        break

    results = model(frame, conf=0.50, verbose=False)

    detected_ambulance = False
    detected_lane = None

    lane_counts = {
        "North": 0,
        "South": 0,
        "East": 0,
        "West": 0
    }

    # Detect objects
    for result in results:
        for box in result.boxes:

            class_id = int(box.cls[0])
            label = model.names[class_id]
            confidence = float(box.conf[0])

            print(f"Detected: {label} | Confidence: {confidence:.2f}")

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Count ordinary vehicles in each lane
            if label == "other_vehicle":

                frame_height, frame_width = frame.shape[:2]

                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                middle_x = frame_width // 2
                middle_y = frame_height // 2

                if abs(center_x - middle_x) > abs(center_y - middle_y):
                    vehicle_lane = "West" if center_x < middle_x else "East"
                else:
                    vehicle_lane = "North" if center_y < middle_y else "South"

                lane_counts[vehicle_lane] += 1

            color = (0, 255, 0)

            # Ambulance detection and lane identification
            if label == "ambulance":

                detected_ambulance = True
                color = (0, 0, 255)

                frame_height, frame_width = frame.shape[:2]

                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                middle_x = frame_width // 2
                middle_y = frame_height // 2

                if abs(center_x - middle_x) > abs(center_y - middle_y):
                    detected_lane = "West" if center_x < middle_x else "East"
                else:
                    detected_lane = "North" if center_y < middle_y else "South"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                frame,
                f"{label}: {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

    # Update detection counters once per frame
    if detected_ambulance:
        detected_frames += 1
        missing_frames = 0
    else:
        missing_frames += 1
        detected_frames = 0

    # Send traffic counts to backend every 2 seconds
    if time.time() - last_count_update >= 2:

        for lane, count in lane_counts.items():

            try:
                requests.post(
                    f"{API_URL}/api/traffic/count",
                    json={
                        "lane": lane,
                        "count": count
                    },
                    timeout=3
                )

            except requests.RequestException as error:
                print("Traffic count update error:", error)

        last_count_update = time.time()

    # Activate emergency after 3 consecutive detections
    if detected_frames >= 3 and not emergency_active:

        try:
            response = requests.post(
                f"{API_URL}/api/emergency/start",
                json={"lane": detected_lane},
                timeout=3
            )

            print("Emergency activated:", response.json())
            emergency_active = True

        except requests.RequestException as error:
            print("Backend connection error:", error)

    # Restore normal traffic after 10 frames without ambulance
    elif missing_frames >= 10 and emergency_active:

        try:
            response = requests.post(
                f"{API_URL}/api/emergency/stop",
                timeout=3
            )

            print("Emergency stopped:", response.json())
            emergency_active = False

        except requests.RequestException as error:
            print("Backend connection error:", error)

    # Display emergency status
    if detected_ambulance:

        cv2.putText(
            frame,
            f"PRIORITY LANE: {detected_lane}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "AMBULANCE DETECTED!",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.imshow("SirenSync AI Camera Monitor", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
