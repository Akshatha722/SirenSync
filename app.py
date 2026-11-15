from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import time

app = FastAPI(
    title="SirenSync",
    description="AI-Powered Smart Traffic Management System",
    version="1.0"
)

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

lanes = ["North", "South", "East", "West"]
signal_duration = 30
start_time = time.monotonic()


def get_signal_status():
    elapsed = int(time.monotonic() - start_time)
    phase = (elapsed // signal_duration) % 4
    remaining = signal_duration - (elapsed % signal_duration)

    current_lane = lanes[phase]

    lane_signals = {
        lane: "GREEN" if lane == current_lane else "RED"
        for lane in lanes
    }

    return current_lane, remaining, lane_signals


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/api/status")
def system_status():
    current_lane, remaining, lane_signals = get_signal_status()

    return {
        "system": "Online",
        "ambulance_detected": False,
        "emergency_active": False,
        "traffic_signal": "GREEN",
        "current_lane": current_lane,
        "remaining_time": remaining,
        "lane_signals": lane_signals
    }