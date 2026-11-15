import cv2
from ultralytics import YOLO

# Load lightweight YOLOv8 model
print("Loading YOLO model...")
model = YOLO("yolov8n.pt")

print("YOLO model loaded successfully!")

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera not available. Please check your webcam.")
    exit()

print("Camera started. Press Q to quit.")

# COCO vehicle classes
vehicle_classes = ["car", "motorcycle", "bus", "truck"]

while True:
    success, frame = camera.read()

    if not success:
        print("Unable to read camera frame.")
        break

    results = model(frame, verbose=False)

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            confidence = float(box.conf[0])

            if True:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"{label}: {confidence:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

    cv2.imshow("SirenSync - Vehicle Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()