import paramiko
import os
import json
import time
import hashlib
import cv2
import queue
import logging
import threading
from termcolor import colored
from django.http import StreamingHttpResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# EC2 instance details
HOSTNAME = "174.129.72.234"
USERNAME = "ubuntu"
KEY_FILE_PATH = r"map_app\static\fazeelec2.pem"

# File paths
MOVEMENTS_FILE_PATH = os.path.expanduser("~/Downloads/movements.txt")
LOCAL_LAT_LON_FILE_PATH = "map_app/static/lon_lat.json"
REMOTE_MOVEMENTS_FILE_PATH = "/home/ubuntu/auto_car_data/movement_command.txt"
REMOTE_LAT_LON_FILE_PATH = "/home/ubuntu/auto_car_data/lon_lat.json"

# Shared resources
frame_queue = queue.Queue()
stop_event = threading.Event()
last_movements_hash = None

class EC2Connection:
    def __init__(self, hostname, username, key_file):
        self.hostname = hostname
        self.username = username
        self.key_file = key_file
        self.ssh_client = None
        self.sftp_client = None

    def connect(self):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(self.hostname, username=self.username, key_filename=self.key_file)
            self.sftp_client = self.ssh_client.open_sftp()
            # logger.info(f"Connected to {self.hostname}")
        except Exception as e:
            # logger.error(f"Failed to connect to EC2: {e}")
            self.close()

    def close(self):
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        # logger.info("EC2 connection closed.")

    def upload_file(self, local_path, remote_path):
        global last_movements_hash
        try:
            current_hash = get_file_hash(local_path)
            if current_hash == last_movements_hash:
                # logger.info("No changes detected in movements.txt. Skipping upload.")
                return
            
            self.sftp_client.put(local_path, remote_path)
            last_movements_hash = current_hash
            os.remove(local_path)
            # logger.info(f"Uploaded {local_path} to EC2 and deleted local copy.")
        except Exception as e:
            logger.error(f"Error uploading file: {e}")

    def download_json(self, remote_path, local_path):
        try:
            with self.sftp_client.open(remote_path, 'r') as remote_file:
                data = json.load(remote_file)
            with open(local_path, "w") as local_file:
                json.dump(data, local_file, indent=4)
            # logger.info(f"Updated {local_path} with data from EC2.")
        except Exception as e:
            logger.error(f"Error downloading JSON file: {e}")


def get_file_hash(file_path):
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        # logger.error(f"Error hashing file {file_path}: {e}")
        return None


# def stream(request):
#     rtmp_url = "rtmp://54.90.141.3/live/stream"
    
#     def generate():
#         cap = cv2.VideoCapture(rtmp_url)
#         cap.set(cv2.CAP_PROP_BUFFERSIZE, 256)
#         cap.set(cv2.CAP_PROP_FPS, 60)
        
#         while not stop_event.is_set():
#             ret, frame = cap.read()
#             if not ret:
#                 logger.warning("Lost connection to stream. Retrying...")
#                 time.sleep(5)
#                 cap = cv2.VideoCapture(rtmp_url)
#                 continue
#             print("Streaming..")
#             _, jpeg = cv2.imencode('.jpg', frame)
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    
#     return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')


def main():
    ec2 = EC2Connection(HOSTNAME, USERNAME, KEY_FILE_PATH)
    ec2.connect()

    if ec2.sftp_client:
        while not stop_event.is_set():
            ec2.upload_file(MOVEMENTS_FILE_PATH, REMOTE_MOVEMENTS_FILE_PATH)
            ec2.download_json(REMOTE_LAT_LON_FILE_PATH, LOCAL_LAT_LON_FILE_PATH)
            time.sleep(1)
        
        ec2.close()
    else:
        logger.error("EC2 connection failed. Exiting.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # logger.info("Stopping script...")
        stop_event.set()
