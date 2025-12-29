import os
import sys
import json
import uuid
import asyncio
import tempfile
from types import SimpleNamespace

import pytest
from httpx import AsyncClient

# Ensure backend package is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app


class FakeRedis:
    def __init__(self):
        self._store = {}

    def set(self, key, value):
        self._store[key] = value

    def get(self, key):
        return self._store.get(key)

    def expire(self, key, seconds):
        # noop for tests
        return True


@pytest.mark.asyncio
async def test_upload_and_status_flow(monkeypatch):
    fake_redis = FakeRedis()

    # Patch redis_client references imported in routes
    import app.routes.jobs as jobs_mod
    import app.routes.upload as upload_mod

    jobs_mod.redis_client = fake_redis
    upload_mod.redis_client = fake_redis

    # Patch get_job_key to use the same prefix
    # Patch process_video_task.delay to simulate immediate completion
    async def fake_delay(**kwargs):
        job_id = kwargs.get('job_id')
        key = jobs_mod.get_job_key(job_id)
        job = json.loads(fake_redis.get(key))
        job['status'] = 'COMPLETED'
        job['progress'] = 100
        job['current_step'] = 'Complete'
        job['output_video_url'] = f"/api/download/{job_id}"
        fake_redis.set(key, json.dumps(job))

    class FakeTask:
        @staticmethod
        def delay(**kwargs):
            # Synchronously apply the fake completion to avoid background timing issues
            job_id = kwargs.get('job_id')
            key = jobs_mod.get_job_key(job_id)
            job = json.loads(fake_redis.get(key))
            job['status'] = 'COMPLETED'
            job['progress'] = 100
            job['current_step'] = 'Complete'
            job['output_video_url'] = f"/api/download/{job_id}"
            fake_redis.set(key, json.dumps(job))

    monkeypatch.setattr('app.tasks.video_tasks.process_video_task', FakeTask)
    # Also replace the reference imported into the upload route module
    upload_mod.process_video_task = FakeTask

    # Create temporary small files to upload
    with tempfile.TemporaryDirectory() as td:
        video_path = os.path.join(td, 'v1.mp4')
        audio_path = os.path.join(td, 'm1.mp3')
        with open(video_path, 'wb') as f:
            f.write(b'0' * 1024)  # 1KB dummy
        with open(audio_path, 'wb') as f:
            f.write(b'0' * 1024)

        async with AsyncClient(app=app, base_url='http://test') as ac:
            # Open files within context so they are closed before tempdir cleanup
            with open(video_path, 'rb') as vf, open(audio_path, 'rb') as af:
                files = [
                    ('videos', ('v1.mp4', vf, 'video/mp4')),
                    ('music', ('m1.mp3', af, 'audio/mpeg')),
                ]

                data = {'style': 'modern_minimal', 'music_start_time': '0', 'music_end_time': '30'}

                resp = await ac.post('/api/upload', files=files, data=data)

            assert resp.status_code == 201
            body = resp.json()
            job_id = body.get('job_id')
            assert job_id

            # Fake task is synchronous; status should be updated immediately

            # Now fetch job status
            r2 = await ac.get(f'/api/jobs/{job_id}')
            assert r2.status_code == 200
            status = r2.json()
            assert status['status'] == 'COMPLETED'
            assert status['progress'] == 100
            assert status['output_video_url'] is not None
