import cv2
from ultralytics import YOLO

model = YOLO("runs/detect/train-2/weights/best.pt")

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera not available")
    exit()

print("Custom SirenSync model started. Press Q to quit.")

while True:
    success, frame = camera.read()

    if not success:
        break

    results = model(frame, conf=0.35, verbose=False)

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(
                frame,
                f"{label}: {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

    cv2.imshow("SirenSync - Custom Ambulance Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()