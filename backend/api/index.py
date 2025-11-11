import os
import sys
from pathlib import Path

# Add the backend directory to Python path so we can import main
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app from main.py
from main import app

# Import Mangum to wrap FastAPI for serverless
from mangum import Mangum

# This is the handler that Vercel will call
handler = Mangum(app)

