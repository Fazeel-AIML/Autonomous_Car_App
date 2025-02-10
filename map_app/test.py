import cv2
import threading
import time

# RTMP stream URL
rtmp_url = "rtmp://54.90.141.3/live/stream"

# Function to handle the stream capture
def capture_stream():
    # Open RTMP stream
    cap = cv2.VideoCapture(rtmp_url)

    if not cap.isOpened():
        print("Error: Could not open the stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame. Reconnecting...")
            cap.release()  # Release the current connection
            cap = cv2.VideoCapture(rtmp_url)  # Reconnect to the stream

            # Retry connection if not successful
            while not cap.isOpened():
                print("Reconnecting to stream...")
                time.sleep(5)  # Wait before retrying the connection
                cap = cv2.VideoCapture(rtmp_url)
            continue  # Retry capturing the frame

        # Process the frame (example)
        cv2.imshow('RTMP Stream', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start the stream capture in a separate thread
stream_thread = threading.Thread(target=capture_stream)
stream_thread.start()

# Wait for the thread to complete
stream_thread.join()
