import os
import sys
from pathlib import Path

# Add the backend directory to Python path so we can import main
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app from main.py
from main import app

# This is the handler that Vercel will call
# Vercel automatically wraps FastAPI apps with ASGI
handler = app

