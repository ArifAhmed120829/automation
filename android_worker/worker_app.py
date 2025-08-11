import pika
import json
import time
import requests
import threading
from datetime import datetime
from .device_config import DeviceConfig
from .twitter_client import TwitterAutomation

class AndroidWorker:
    def __init__(self):
        self.config = DeviceConfig()
        self.twitter_client = None
        self.registered = False
        
    def register_device(self):
        """Register this device with the server"""
        try:
            response = requests.post(
                f"{self.config.SERVER_URL}/register-device",
                json={
                    "device_id": self.config.DEVICE_ID,
                    "device_name": self.config.DEVICE_NAME,
                    "twitter_username": self.config.TWITTER_USERNAME
                }
            )
            
            if response.status_code == 200:
                self.registered = True
                result = response.json()
                print(f"✅ Device registered: {result['message']}")
                print(f"📱 Device ID: {self.config.DEVICE_ID}")
                print(f"📧 Twitter: @{self.config.TWITTER_USERNAME}")
                print(f"🔄 Queue: {result['queue_name']}")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def setup_twitter_client(self):
        """Setup Twitter automation client"""
        if not self.config.TWITTER_USERNAME or not self.config.TWITTER_PASSWORD:
            print("❌ Twitter credentials not configured!")
            return False
        
        self.twitter_client = TwitterAutomation(
            self.config.TWITTER_USERNAME,
            self.config.TWITTER_PASSWORD
        )
        
        print("🐦 Logging into Twitter...")
        if self.twitter_client.login():
            print("✅ Twitter login successful")
            return True
        else:
            print("❌ Twitter login failed")
            return False
    
    def process_job(self, job_data):
        """Process a Twitter job"""
        job_id = job_data["job_id"]
        tweet_url = job_data["tweet_url"]
        action = job_data["action"]
        device_id = job_data["device_id"]
        
        print(f"\n🔄 Processing Job {job_id}")
        print(f"📱 Device: {device_id}")
        print(f"🐦 Tweet: {tweet_url}")
        print(f"⚡ Action: {action}")
        
        # Report job result
        success = False
        error_message = None
        
        try:
            if action == "like":
                result = self.twitter_client.like_tweet(tweet_url)
                success = result["success"]
                if not success:
                    error_message = result.get("error", "Unknown error")
            else:
                error_message = f"Unsupported action: {action}"
            
        except Exception as e:
            error_message = str(e)
        
        # Report result to server
        self.report_job_result(job_id, success, error_message)
        
        if success:
            print(f"✅ Job {job_id} completed successfully")
        else:
            print(f"❌ Job {job_id} failed: {error_message}")
    
    def report_job_result(self, job_id: int, success: bool, error_message: str = None):
        """Report job result to server"""
        try:
            response = requests.post(
                f"{self.config.SERVER_URL}/job-result",
                json={
                    "job_id": job_id,
                    "device_id": self.config.DEVICE_ID,
                    "success": success,
                    "error_message": error_message
                }
            )
            
            if response.status_code != 200:
                print(f"⚠️ Failed to report job result: {response.text}")
                
        except Exception as e:
            print(f"⚠️ Error reporting job result: {e}")
    
    def job_callback(self, ch, method, properties, body):
        """Handle incoming job messages"""
        try:
            job_data = json.loads(body)
            self.process_job(job_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"❌ Error processing job: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def heartbeat_worker(self):
        """Send periodic heartbeats to keep device status updated"""
        while True:
            try:
                time.sleep(self.config.HEARTBEAT_INTERVAL)
                # Heartbeat is sent via job result reporting mechanism
                # You could add a dedicated heartbeat endpoint if needed
            except Exception as e:
                print(f"⚠️ Heartbeat error: {e}")
    
    def start(self):
        """Start the Android worker"""
        print(f"🚀 Starting Android Worker")
        print(f"📱 Device ID: {self.config.DEVICE_ID}")
        print(f"🌐 Server: {self.config.SERVER_URL}")
        
        # Register device
        if not self.register_device():
            print("❌ Failed to register device. Exiting.")
            return
        
        # Setup Twitter client
        if not self.setup_twitter_client():
            print("❌ Failed to setup Twitter client. Exiting.")
            return
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.heartbeat_worker, daemon=True)
        heartbeat_thread.start()
        
        # Connect to RabbitMQ and listen for jobs
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.config.RABBITMQ_URL))
            channel = connection.channel()
            
            # Listen to device-specific queue
            queue_name = f"device_{self.config.DEVICE_ID}"
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=self.job_callback
            )
            
            print(f"🎯 Listening for jobs on queue: {queue_name}")
            print("⏳ Waiting for jobs... Press CTRL+C to exit")
            
            channel.start_consuming()
            
        except KeyboardInterrupt:
            print("\n🛑 Worker stopping...")
            channel.stop_consuming()
            connection.close()
            if self.twitter_client:
                self.twitter_client.close()
            print("✅ Worker stopped gracefully")
        except Exception as e:
            print(f"❌ Worker error: {e}")

if __name__ == "__main__":
    worker = AndroidWorker()
    worker.start()
