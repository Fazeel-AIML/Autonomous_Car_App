from django.http import JsonResponse, StreamingHttpResponse
import json
import logging
from django.shortcuts import render
import time
import zlib
import os
from django.http import HttpResponse
from django.core.cache import cache
from io import BytesIO
from PIL import Image
# from services.aws_server import stream
import cv2

# Set up logging
logger = logging.getLogger(__name__)

# Path to the file where lat_lon is saved
DATA_FILE_PATH = r'map_app\static\lon_lat.json'

def load_gps_data():
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            gps_data = json.load(f)
            
            latitude = gps_data.get('latitude', 33.00000)  # Default to 33.00000 if missing
            longitude = gps_data.get('longitude', 73.00000)  # Default to 73.00000 if missing
            if longitude is None and latitude is None:
                longitude = 71.755825
                latitude = 29.382374
            speed = gps_data.get('speed', 0.0)
            satellite = gps_data.get('satellite', 0)
            altitude = gps_data.get('altitude', 0.0)
            time = gps_data.get('time', '00:00:00 UTC')
            return latitude, longitude, speed, satellite, altitude, time
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading GPS data: {e}")
        return 33.00000, 73.00000, 0.0, 0, 0.0, '00:00:00 UTC'  # Default values on error

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')

import subprocess
import cv2
import time
import numpy as np
from collections import deque
from django.http import StreamingHttpResponse

def video_stream():
    rtmp_url = "rtmp://174.129.72.234/live/stream"

    def open_stream():
        """Keep trying to open the RTMP stream indefinitely."""
        retries = 0
        while True:
            cap = cv2.VideoCapture(rtmp_url)
            # Set buffer size to 512KB (512 * 1024 bytes)
            #cap.set(cv2.CAP_PROP_BUFFERSIZE, 512 * 1024)
            if cap.isOpened():
                print("Connected to stream.")
                return cap
            print(f"Error: Could not open stream. Retrying ({retries + 1})...")
            time.sleep(3)  # Avoid rapid retries
            retries += 1

    cap = open_stream()
    frame_buffer = deque(maxlen=1)  # Keep only the latest frame

    while True:
        success, frame = cap.read()

        if not success:
            print("Stream lost. Attempting reconnection...")
            cap.release()
            cap = open_stream()
            continue  # Skip this iteration and retry reading

        frame_buffer.append(frame)

        if frame_buffer:
            _, buffer = cv2.imencode('.jpg', frame_buffer[-1], [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            print("Streaming...")

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()  # Cleanup when exiting (unlikely to reach)

def stream_view(request):
    return StreamingHttpResponse(video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')



def map_view(request):
    latitude, longitude, speed, satellite, altitude, time = load_gps_data()
    return render(request, 'home.html', {
        'latitude': latitude,
        'longitude': longitude,
        'speed': speed,
        'satellite': satellite,
        'altitude': altitude,
        'time': time
    })

def gps_data(request):
    latitude, longitude, speed, satellite, altitude, time = load_gps_data()
    return JsonResponse({
        'latitude': latitude,
        'longitude': longitude,
        'speed': speed,
        'satellite': satellite,
        'altitude': altitude,
        'time': time
    })