
import cv2

# RTMP Stream URL (Replace with your EC2 instance IP)
RTMP_STREAM_URL = "rtmp://174.129.72.234/live/stream"

# Open RTMP Stream with OpenCV
cap = cv2.VideoCapture(RTMP_STREAM_URL)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to receive frame. Exiting...")
        break

    cv2.imshow("RTMP Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
