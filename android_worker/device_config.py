import os
import uuid
from datetime import datetime

class DeviceConfig:
    def __init__(self):
        self.DEVICE_ID = os.getenv("DEVICE_ID", f"android_{uuid.uuid4().hex[:8]}")
        self.DEVICE_NAME = os.getenv("DEVICE_NAME", f"Android_Device_{self.DEVICE_ID[-4:]}")
        self.TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")  # Must be set!
        self.TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")  # Must be set!
        
        # Server connection
        self.SERVER_URL = os.getenv("SERVER_URL", "http://192.168.1.100:8000")
        self.RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:password123@192.168.1.100:5672/")
        
        # Worker settings
        self.HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "60"))  # seconds
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
