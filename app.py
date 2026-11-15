from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SirenSync",
    description="AI-Powered Smart Traffic Management System",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return {
        "project": "SirenSync",
        "message": "SirenSync Backend is Running!",
        "status": "Active"
    }


@app.get("/api/status")
def system_status():
    return {
        "system": "Online",
        "ambulance_detected": False,
        "emergency_active": False,
        "traffic_signal": "GREEN",
        "current_lane": "North",
        "remaining_time": 30
    }