# your_app/apps.py
import threading
from django.apps import AppConfig
from services.aws_server import main  # Adjust the import path as needed

class MapAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'map_app'

    def ready(self):
        # Start the socket server in a separate thread
        thread = threading.Thread(target=main)
        thread.daemon = True
        thread.start()
        print("[Django] Socket server started.")