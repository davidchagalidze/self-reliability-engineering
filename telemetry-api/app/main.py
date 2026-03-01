from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="SRE Telemetry API")

# Connect the routes from routes.py
app.include_router(router)