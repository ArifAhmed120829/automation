from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import Device, SessionLocal
import pika
import json
from .config import Config

class DeviceManager:
    def __init__(self):
        self.rabbitmq_connection = None
        
    def get_db(self):
        return SessionLocal()
    
    def register_device(self, device_id: str, device_name: str, twitter_username: str) -> dict:
        """Register a new Android device"""
        db = self.get_db()
        try:
            # Check if device already exists
            existing_device = db.query(Device).filter(Device.device_id == device_id).first()
            
            if existing_device:
                # Update existing device
                existing_device.device_name = device_name
                existing_device.twitter_username = twitter_username
                existing_device.status = "online"
                existing_device.last_seen = datetime.utcnow()
                db.commit()
                return {"status": "updated", "device": existing_device}
            else:
                # Create new device
                new_device = Device(
                    device_id=device_id,
                    device_name=device_name,
                    twitter_username=twitter_username,
                    status="online"
                )
                db.add(new_device)
                db.commit()
                db.refresh(new_device)
                
                # Create device-specific queue
                self._create_device_queue(device_id)
                
                return {"status": "registered", "device": new_device}
                
        finally:
            db.close()
    
    def get_online_devices(self) -> list:
        """Get all online devices"""
        db = self.get_db()
        try:
            # Consider devices online if last seen within timeout period
            cutoff_time = datetime.utcnow() - timedelta(seconds=Config.DEVICE_TIMEOUT)
            devices = db.query(Device).filter(
                Device.last_seen >= cutoff_time,
                Device.status.in_(["online", "working"])
            ).all()
            return devices
        finally:
            db.close()
    
    def _create_device_queue(self, device_id: str):
        """Create RabbitMQ queue for specific device"""
        try:
            connection = pika.BlockingConnection(pika.URLParameters(Config.RABBITMQ_URL))
            channel = connection.channel()
            
            queue_name = f"device_{device_id}"
            channel.queue_declare(queue=queue_name, durable=True)
            
            connection.close()
        except Exception as e:
            print(f"Error creating queue for device {device_id}: {e}")
    
    def distribute_job_to_devices(self, job_id: int, tweet_url: str, tweet_id: str, action: str):
        """Distribute job to all online devices"""
        online_devices = self.get_online_devices()
        
        if not online_devices:
            raise Exception("No online devices available")
        
        try:
            connection = pika.BlockingConnection(pika.URLParameters(Config.RABBITMQ_URL))
            channel = connection.channel()
            
            for device in online_devices:
                queue_name = f"device_{device.device_id}"
                
                message = {
                    "job_id": job_id,
                    "tweet_url": tweet_url,
                    "tweet_id": tweet_id,
                    "action": action,
                    "device_id": device.device_id,
                    "assigned_at": datetime.utcnow().isoformat()
                }
                
                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
            
            connection.close()
            return len(online_devices)
            
        except Exception as e:
            raise Exception(f"Failed to distribute job: {e}")

