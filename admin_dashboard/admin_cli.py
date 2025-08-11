import requests
import sys
import json
import time

class DeviceFarmCLI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def list_devices(self):
        """List all registered devices"""
        try:
            response = requests.get(f"{self.base_url}/devices")
            if response.status_code == 200:
                data = response.json()
                print(f"\n📱 Total Devices: {data['total_devices']}")
                print("=" * 80)
                
                for device in data['online_devices']:
                    print(f"📱 Device: {device['device_name']} ({device['device_id']})")
                    print(f"   🐦 Twitter: @{device['twitter_username']}")
                    print(f"   📊 Status: {device['status']}")
                    print(f"   ✅ Completed: {device['jobs_completed']}")
                    print(f"   ❌ Failed: {device['jobs_failed']}")
                    print(f"   🕐 Last Seen: {device['last_seen']}")
                    print("-" * 40)

             else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Connection error: {e}")

    def create_mass_job(self, tweet_url: str, action: str = "like"):
        """Create a job for ALL devices"""
        try:
            response = requests.post(
                f"{self.base_url}/create-mass-job",
                json={
                    "tweet_url": tweet_url,
                    "action": action
                }
            )

            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Mass job created successfully!")
                print(f"🆔 Job ID: {result['job_id']}")
                print(f"🐦 Tweet: {result['tweet_url']}")
                print(f"⚡ Action: {result['action']}")
                print(f"📱 Devices Targeted: {result['devices_targeted']}")
                print(f"💬 {result['message']}")
                return result['job_id']
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Connection error: {e}")
            return None

    def get_job_status(self, job_id: int):
        """Get detailed job status"""
        try:
            response = requests.get(f"{self.base_url}/job-status/{job_id}")
            if response.status_code == 200:
                job = response.json()

                print(f"\n📊 Job Status Report")
                print("=" * 50)
                print(f"🆔 Job ID: {job['job_id']}")
                print(f"🐦 Tweet: {job['tweet_url']}")
                print(f"⚡ Action: {job['action']}")
                print(f"📊 Status: {job['status']}")
                print(f"🕐 Created: {job['created_at']}")
                print(f"🎯 Target Devices: {job['target_devices']}")
                print(f"✅ Completed: {job['completed_devices']}")
                print(f"❌ Failed: {job['failed_devices']}")

                print(f"\n📱 Device Results:")
                print("-" * 50)

                for device_result in job['device_results']:
                    status_emoji = "✅" if device_result['status'] == "completed" else "❌" if device_result['status'] == "failed" else "⏳"
                    print(f"{status_emoji} {device_result['device_id']}: {device_result['status']}")
                    if device_result['error_message']:
                        print(f"   Error: {device_result['error_message']}")

            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Connection error: {e}")

    def monitor_job(self, job_id: int, interval: int = 5):
        """Monitor job progress in real-time"""
        print(f"🔄 Monitoring job {job_id} (updating every {interval}s)...")
        print("Press Ctrl+C to stop monitoring\n")

        try:
            while True:
                self.get_job_status(job_id)
                time.sleep(interval)
                print("\n" + "="*50 + " REFRESHING " + "="*50 + "\n")
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

def main():
    cli = DeviceFarmCLI()

    if len(sys.argv) < 2:
        print("🚀 Twitter Device Farm - Admin CLI")
        print("="*50)
        print("Usage:")
        print("  python admin_cli.py devices                    # List all devices")
        print("  python admin_cli.py attack <tweet_url>         # Send job to ALL devices")
        print("  python admin_cli.py status <job_id>            # Check job status")
        print("  python admin_cli.py monitor <job_id>           # Monitor job real-time")
        print()
        print("Examples:")
        print("  python admin_cli.py attack 'https://x.com/narendramodi/status/1954463218958553492'")
        print("  python admin_cli.py status 1")
        print("  python admin_cli.py monitor 1")
        return

    command = sys.argv[1]

    if command == "devices":
        cli.list_devices()

    elif command == "attack":
        if len(sys.argv) < 3:
            print("❌ Please provide a tweet URL")
            return

        tweet_url = sys.argv[2]
        action = sys.argv[3] if len(sys.argv) > 3 else "like"

        print(f"🚀 Launching mass {action} attack on:")
        print(f"🎯 Target: {tweet_url}")

        job_id = cli.create_mass_job(tweet_url, action)

        if job_id:
            print(f"\n🔄 Auto-monitoring job {job_id}...")
            time.sleep(2)
            cli.monitor_job(job_id, interval=3)

    elif command == "status":
        if len(sys.argv) < 3:
            print("❌ Please provide a job ID")
            return

        job_id = int(sys.argv[2])
        cli.get_job_status(job_id)

    elif command == "monitor":
        if len(sys.argv) < 3:
            print("❌ Please provide a job ID")
            return

        job_id = int(sys.argv[2])
        interval = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        cli.monitor_job(job_id, interval)

    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()

