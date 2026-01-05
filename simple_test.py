"""
Simple test script for video processing pipeline
"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Mock the database functions to avoid Redis dependency
class MockJobs:
    @staticmethod
    def update_job_progress(job_id, progress, message):
        print(f"Progress {progress}%: {message}")
    
    @staticmethod 
    def mark_job_complete(job_id, download_url):
        print(f"Job {job_id} completed: {download_url}")
        
    @staticmethod
    def mark_job_failed(job_id, error_message):
        print(f"Job {job_id} failed: {error_message}")

# Patch the jobs module before importing video processor
sys.modules['app.routes.jobs'] = MockJobs()

try:
    from app.services.video_processor import VideoProcessor
    print("✅ VideoProcessor imported successfully")
    
    # Test basic functionality
    processor = VideoProcessor()
    print("✅ VideoProcessor instantiated successfully")
    
    print("🎉 All basic tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()