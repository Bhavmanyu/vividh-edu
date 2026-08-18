"""
Vercel Serverless Functions adapter for the FastAPI app.
This lets the entire FastAPI backend run on Vercel's free tier.

Usage: vercel.json points 'builds' to this file.
"""
from mangum import Mangum
from .main import app

handler = Mangum(app, lifespan="off")
