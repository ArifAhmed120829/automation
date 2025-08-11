# 🚀 Twitter Device Farm - 50 Android Automation System

A distributed system for managing 50+ Android devices to perform Twitter automation tasks like mass liking, retweeting, and commenting.

## 🏗️ Architecture

```
Admin Dashboard (Web/CLI)
    │ POST: "Like tweet X"
    ▼
FastAPI Server (Computer/Cloud)
    │ creates 50 jobs (one per device)
    ▼
RabbitMQ (Computer/Cloud)
    │ distributes jobs to device queues
    ▼
┌─────────┬─────────┬─────────┬─────┐
│Android 1│Android 2│Android 3│ ... │ ← 50 Android Workers
│Worker   │Worker   │Worker   │     │
└─────────┴─────────┴─────────┴─────┘
    │         │         │         │
    ▼         ▼         ▼         ▼
Real Twitter API (50 different accounts)
```

## 🚀 Quick Setup

### 1. Server Setup (Your Computer/Cloud)

```bash
# Install dependencies
pip install -r requirements.txt

# Start infrastructure
docker-compose up -d

# Start FastAPI server
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### 2. Android Device Setup (Each Device)

**Install Termux on each Android device:**
```bash
# In Termux on each device:
pkg update && pkg upgrade
pkg install python git
pip install requests pika selenium

# Clone worker code
git clone <your-repo>
cd twitter_automation_50_devices/android_worker

# Configure device (IMPORTANT!)
export DEVICE_ID="android_device_01"  # Unique for each device
export DEVICE_NAME="Galaxy_S21_01"    # Descriptive name
export TWITTER_USERNAME="user01"      # Twitter account for this device
export TWITTER_PASSWORD="pass01"      # Twitter password
export SERVER_URL="http://YOUR_SERVER_IP:8000"  # Your server IP

# Start worker
python worker_app.py
```

### 3. Admin Interface

**CLI Commands:**
```bash
# List connected devices
python admin_dashboard/admin_cli.py devices

# Launch attack on ALL devices
python admin_dashboard/admin_cli.py attack "https://x.com/narendramodi/status/1954463218958553492"

# Monitor job progress
python admin_dashboard/admin_cli.py monitor 1
```

**Web Dashboard:**
- Open `admin_dashboard/web_dashboard.html` in browser
- Real-time device monitoring and job management

## 📱 Device Configuration Examples

### Device 1:
```bash
export DEVICE_ID="android_01"
export DEVICE_NAME="Samsung_Galaxy_01"
export TWITTER_USERNAME="twitterbot01"
export TWITTER_PASSWORD="securepass01"
```

### Device 2:
```bash
export DEVICE_ID="android_02"  
export DEVICE_NAME="Xiaomi_Phone_02"
export TWITTER_USERNAME="twitterbot02"
export TWITTER_PASSWORD="securepass02"
```

### Device N (up to 50):
```bash
export DEVICE_ID="android_50"
export DEVICE_NAME="OnePlus_Device_50"
export TWITTER_USERNAME="twitterbot50"
export TWITTER_PASSWORD="securepass50"
```

## 🎯 Usage Examples

### Mass Like Attack:
```bash
python admin_cli.py attack "https://x.com/elonmusk/status/123456789"
```
**Result**: All 50 devices automatically like the tweet

### Mass Retweet:
```bash
python admin_cli.py attack "https://x.com/user/status/123456789" retweet
```

### Monitor Progress:
```bash
python admin_cli.py monitor 1
```
**Output**:
```
📊 Job 1: 85% complete (✅42 ❌1/50) - Status: processing
📊 Job 1: 100% complete (✅48 ❌2/50) - Status: completed
🎉 Job completed! Final: ✅48 ❌2/50
```

## 🔧 Key Features

### ✅ **Device Management**
- Auto device registration
- Real-time status monitoring  
- Device-specific job queues
- Heartbeat monitoring

### ✅ **Job Distribution**
- One command → 50 devices
- Real-time progress tracking
- Individual device results
- Error handling & retries

### ✅ **Twitter Automation**
- Real browser automation (Selenium)
- Human-like behavior simulation
- Multiple account management
- Anti-detection measures

### ✅ **Monitoring & Control**
- Web dashboard
- CLI interface
- Real-time logs
- Success/failure tracking

## 📊 Dashboard Features

- **Device Overview**: See all 50 devices status
- **Mass Attack Panel**: Launch coordinated attacks
- **Real-time Monitoring**: Track job progress
- **Statistics**: Success rates, completion times
- **Error Logs**: Debug failed attempts

## ⚠️ Important Notes

### Security & Legal:
- Each device needs unique Twitter accounts
- Respect Twitter's rate limits and ToS  
- Use residential IP addresses
- Implement proper delays between actions

### Setup Requirements:
- **50 Android devices** (phones/tablets/emulators)
- **50 unique Twitter accounts** 
- **Reliable internet** for all devices
- **Central server** (your computer/cloud)

### Device Management:
- Each device gets unique ID and queue
- Automatic reconnection on network issues
- Device health monitoring
- Remote job distribution

## 🚀 Production Tips

1. **Use different IP addresses** for devices (mobile data, WiFi, VPN)
2. **Stagger device startup** to avoid detection
3. **Monitor rate limits** across all accounts
4. **Implement random delays** between actions
5. **Use proxy rotation** if needed
6. **Keep device accounts active** with regular organic activity

## 🔥 What You Can Achieve

With this system you can:
- **Mass like** any tweet with 50 devices instantly
- **Coordinate retweets** across your device farm  
- **Boost engagement** on target content
- **Monitor effectiveness** in real-time
- **Scale operations** easily

This is a **production-ready** distribute

[200~This is a **production-ready** distributed automation system that gives you complete control over your Android device army! 🔥
# automation
