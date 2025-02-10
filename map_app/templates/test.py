import cv2

# RTMP stream URL
rtmp_url = "rtmp://54.90.141.3/live/stream"

# Open RTMP stream
cap = cv2.VideoCapture(rtmp_url)

if not cap.isOpened():
    print("Error: Could not open the stream.")
else:
    # Set buffer size and timeout settings
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 256)  # Increase buffer size to handle more frames
    cap.set(cv2.CAP_PROP_FPS, 60)         # Set the FPS if known

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Process the frame (example)
        cv2.imshow('RTMP Stream', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
