from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .config import Config

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, nullable=False)
    device_name = Column(String, nullable=False)
    twitter_username = Column(String, nullable=False)
    status = Column(String, default="offline")  # online, offline, working, error
    last_seen = Column(DateTime, default=datetime.utcnow)
    registered_at = Column(DateTime, default=datetime.utcnow)
    jobs_completed = Column(Integer, default=0)
    jobs_failed = Column(Integer, default=0)

class TwitterJob(Base):
    __tablename__ = "twitter_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    tweet_url = Column(String, nullable=False)
    tweet_id = Column(String, nullable=False)
    action = Column(String, default="like")  # like, retweet, reply
    status = Column(String, default="pending")  # pending, distributed, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    target_devices = Column(Integer, default=0)  # How many devices should process this
    completed_devices = Column(Integer, default=0)  # How many completed
    failed_devices = Column(Integer, default=0)  # How many failed

class DeviceJob(Base):
    __tablename__ = "device_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, nullable=False)
    device_id = Column(String, nullable=False)
    status = Column(String, default="assigned")  # assigned, processing, completed, failed
    assigned_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)
