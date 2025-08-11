from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import re
from typing import List, Optional
from .database import SessionLocal, TwitterJob, Device, DeviceJob
from .device_manager import DeviceManager
from datetime import datetime

app = FastAPI(title="Twitter Device Farm API", version="2.0.0")
device_manager = DeviceManager()

# Pydantic models
class DeviceRegistration(BaseModel):
    device_id: str
    device_name: str
    twitter_username: str

class TwitterJobRequest(BaseModel):
    tweet_url: str
    action: str = "like"

class JobResult(BaseModel):
    device_id: str
    job_id: int
    success: bool
    error_message: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extract_tweet_id(tweet_url: str) -> str:
    """Extract tweet ID from Twitter URL"""
    patterns = [
        r'https?://(?:www\.|mobile\.)?(?:twitter\.com|x\.com)/.+/status/(\d+)',
        r'/status/(\d+)',
        r'(\d{15,})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, tweet_url)
        if match:
            return match.group(1)
    return None

@app.get("/")
async def root():
    return {"message": "Twitter Device Farm API", "status": "running", "devices": "ready"}

@app.post("/register-device")
async def register_device(device_reg: DeviceRegistration):
    """Register an Android device"""
    try:
        result = device_manager.register_device(
            device_reg.device_id,
            device_reg.device_name,
            device_reg.twitter_username
        )
        
        return {
            "success": True,
            "message": f"Device {result['status']} successfully",
            "device_id": device_reg.device_id,
            "queue_name": f"device_{device_reg.device_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices")
async def list_devices():
    """List all registered devices"""
    devices = device_manager.get_online_devices()
    return {
        "total_devices": len(devices),
        "online_devices": [
            {
                "device_id": d.device_id,
                "device_name": d.device_name,
                "twitter_username": d.twitter_username,
                "status": d.status,
                "jobs_completed": d.jobs_completed,
                "jobs_failed": d.jobs_failed,
                "last_seen": d.last_seen.isoformat()
            }
            for d in devices
        ]
    }

@app.post("/create-mass-job")
async def create_mass_job(job_request: TwitterJobRequest, db: Session = Depends(get_db)):
    """Create a job that will be sent to ALL online devices"""
    
    # Extract tweet ID
    tweet_id = extract_tweet_id(job_request.tweet_url)
    if not tweet_id:
        raise HTTPException(status_code=400, detail="Invalid Twitter URL")
    
    # Get online devices
    online_devices = device_manager.get_online_devices()
    if not online_devices:
        raise HTTPException(status_code=400, detail="No online devices available")
    
    # Create master job
    master_job = TwitterJob(
        tweet_url=job_request.tweet_url,
        tweet_id=tweet_id,
        action=job_request.action,
        target_devices=len(online_devices),
        status="distributing"
    )
    db.add(master_job)
    db.commit()
    db.refresh(master_job)
    
    try:
        # Distribute to all devices
        distributed_count = device_manager.distribute_job_to_devices(
            master_job.id,
            job_request.tweet_url,
            tweet_id,
            job_request.action
        )
        
        # Create individual device jobs tracking
        for device in online_devices:
            device_job = DeviceJob(
                job_id=master_job.id,
                device_id=device.device_id,
                status="assigned"
            )
            db.add(device_job)
        
        master_job.status = "distributed"
        db.commit()
        
        return {
            "success": True,
            "job_id": master_job.id,
            "tweet_url": job_request.tweet_url,
            "tweet_id": tweet_id,
            "action": job_request.action,
            "devices_targeted": distributed_count,
            "message": f"Job distributed to {distributed_count} devices"
        }
        
    except Exception as e:
        master_job.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to distribute job: {str(e)}")

@app.post("/job-result")
async def report_job_result(result: JobResult, db: Session = Depends(get_db)):
    """Device reports job completion result"""
    
    # Update device job status
    device_job = db.query(DeviceJob).filter(
        DeviceJob.job_id == result.job_id,
        DeviceJob.device_id == result.device_id
    ).first()
    
    if not device_job:
        raise HTTPException(status_code=404, detail="Device job not found")
    
    # Update device job
    device_job.status = "completed" if result.success else "failed"
    device_job.completed_at = datetime.utcnow()
    if not result.success:
        device_job.error_message = result.error_message
    
    # Update device statistics
    device = db.query(Device).filter(Device.device_id == result.device_id).first()
    if device:
        if result.success:
            device.jobs_completed += 1
        else:
            device.jobs_failed += 1
        device.last_seen = datetime.utcnow()
    
    # Update master job statistics
    master_job = db.query(TwitterJob).filter(TwitterJob.id == result.job_id).first()
    if master_job:
        if result.success:
            master_job.completed_devices += 1
        else:
            master_job.failed_devices += 1
        
        # Check if all devices completed
        if master_job.completed_devices + master_job.failed_devices >= master_job.target_devices:
            master_job.status = "completed"
    
    db.commit()
    
    return {"success": True, "message": "Job result recorded"}

@app.get("/job-status/{job_id}")
async def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """Get detailed job status"""
    
    master_job = db.query(TwitterJob).filter(TwitterJob.id == job_id).first()
    if not master_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    device_jobs = db.query(DeviceJob).filter(DeviceJob.job_id == job_id).all()
    
    return {
        "job_id": job_id,
        "tweet_url": master_job.tweet_url,
        "action": master_job.action,
        "status": master_job.status,
        "created_at": master_job.created_at.isoformat(),
        "target_devices": master_job.target_devices,
        "completed_devices": master_job.completed_devices,
        "failed_devices": master_job.failed_devices,
        "device_results": [
            {
                "device_id": dj.device_id,
                "status": dj.status,
                "assigned_at": dj.assigned_at.isoformat(),
                "completed_at": dj.completed_at.isoformat() if dj.completed_at else None,
                "error_message": dj.error_message
            }
            for dj in device_jobs
        ]
    }
