import sys
import os
import pytest
from httpx import AsyncClient
import uuid

# Ensure backend package is importable when tests run from the backend folder
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app


@pytest.mark.asyncio
async def test_get_job_invalid_id():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get('/api/jobs/not-a-uuid')
    assert r.status_code == 400
    payload = r.json()
    assert payload.get('error') is True
    assert 'Invalid job ID' in payload.get('message', '') or 'Invalid job ID format' in payload.get('message', '')


@pytest.mark.asyncio
async def test_download_missing_file():
    job_id = str(uuid.uuid4())
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get(f'/api/download/{job_id}')
    assert r.status_code == 404
    payload = r.json()
    assert payload.get('error') is True
    assert 'Output video not found' in payload.get('message') or 'not found' in payload.get('message')


@pytest.mark.asyncio
async def test_upload_validation_missing_files():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post('/api/upload', data={})
    # FastAPI will return 422 for missing required form fields
    assert r.status_code == 422
    payload = r.json()
    assert payload.get('error') is True
    assert 'Invalid request' in payload.get('message') or 'value is not a valid' in payload.get('message')
