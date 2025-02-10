from django.core.management.base import BaseCommand
from services.aws_server import start_server  # Adjust the import path as needed

class Command(BaseCommand):
    help = 'Start the socket server'

    def handle(self, *args, **kwargs):
        print("[Django] Starting the socket server...")
        start_server()
