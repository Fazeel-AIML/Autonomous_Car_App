import cv2
import threading
import time

# RTMP stream URL
rtmp_url = "rtmp://174.129.72.234/live/stream"

# Function to handle the stream capture
def capture_stream():
    # Open RTMP stream with buffer size and FPS settings
    cap = cv2.VideoCapture(rtmp_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 512000)  # Set buffer size to 3000k
    cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS to 30

    if not cap.isOpened():
        print("Error: Could not open the stream.")
        return

    retry_delay = 5  # Initial delay for reconnection

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame. Reconnecting...")

            cap.release()  # Release the current connection
            time.sleep(retry_delay)  # Wait before reconnecting
            cap = cv2.VideoCapture(rtmp_url)

            # Exponential backoff for reconnection
            while not cap.isOpened():
                print(f"Reconnecting in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)  # Max delay of 60 sec
                cap = cv2.VideoCapture(rtmp_url)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 3000)
                cap.set(cv2.CAP_PROP_FPS, 30)

            retry_delay = 5  # Reset delay after successful reconnection
            continue  # Retry capturing the frame

        # Display the frame
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
