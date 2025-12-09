# src/tests/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
import httpx
from httpx import ASGITransport
from src.main import app
import os

# Indicar al sistema y al mailer que estamos en modo testing
os.environ.setdefault("TESTING", "1")

@pytest.fixture(scope="module")
async def async_client():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
