import cv2
import subprocess

RTMP_URL = "rtmp://174.129.72.234/live/stream"

cap = cv2.VideoCapture(0)

ffmpeg_cmd = [
    "ffmpeg",
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-s", "640x480",
    "-r", "30",
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-f", "flv",
    RTMP_URL
]

# Start FFmpeg and capture errors
process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Frame capture failed!")
        break

    try:
        process.stdin.write(frame.tobytes())  # Send frame to FFmpeg
    except BrokenPipeError:
        print("FFmpeg process terminated unexpectedly!")
        break

# Capture FFmpeg errors
stderr_output = process.stderr.read().decode()
print("FFmpeg Error Log:", stderr_output)

cap.release()
if process.stdin:
    process.stdin.close()
process.wait()
