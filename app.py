from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import time
import csv
import os
from datetime import datetime

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

emergency_active = False
emergency_lane = None
saved_signal_state = None
LOG_FILE = "logs/emergency_events.csv"


class EmergencyRequest(BaseModel):
    lane: str
def log_emergency(event_data):
    os.makedirs("logs", exist_ok=True)

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "event",
                "date_time",
                "ambulance_lane",
                "previous_signal_lane"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(event_data)

def get_normal_signal():
    elapsed = int(time.monotonic() - start_time)
    phase = (elapsed // signal_duration) % 4
    remaining = signal_duration - (elapsed % signal_duration)

    return lanes[phase], remaining


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/api/status")
def system_status():
    if emergency_active:
        current_lane = emergency_lane
        remaining = 0

    else:
        current_lane, remaining = get_normal_signal()

    lane_signals = {
        lane: "GREEN" if lane == current_lane else "RED"
        for lane in lanes
    }

    return {
        "system": "Online",
        "ambulance_detected": emergency_active,
        "emergency_active": emergency_active,
        "traffic_signal": "GREEN",
        "current_lane": current_lane,
        "remaining_time": remaining,
        "lane_signals": lane_signals
    }


@app.post("/api/emergency/start")
def start_emergency(data: EmergencyRequest):
    global emergency_active, emergency_lane, saved_signal_state

    if data.lane not in lanes:
        return {"error": "Invalid lane"}

    if emergency_active:
        return {"message": "An emergency is already active"}

    current_lane, remaining = get_normal_signal()

    saved_signal_state = {
        "lane": current_lane,
        "remaining": remaining
    }

    emergency_lane = data.lane
    emergency_active = True

    log_emergency({
        "event": "EMERGENCY_STARTED",
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ambulance_lane": emergency_lane,
        "previous_signal_lane": saved_signal_state["lane"]
    })
    return {
        "message": "Emergency priority activated",
        "priority_lane": emergency_lane,
        "signal": "GREEN",
        "saved_signal": saved_signal_state
    }


@app.post("/api/emergency/stop")
def stop_emergency():
    global emergency_active, emergency_lane
    global saved_signal_state, start_time

    if not emergency_active:
        return {"message": "No emergency is active"}

    saved_lane = saved_signal_state["lane"]
    saved_remaining = saved_signal_state["remaining"]
    log_emergency({
        "event": "EMERGENCY_STOPPED",
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ambulance_lane": emergency_lane,
        "previous_signal_lane": saved_lane
    })
    phase = lanes.index(saved_lane)

    elapsed_before_emergency = (
        phase * signal_duration
        + signal_duration
        - saved_remaining
    )

    start_time = time.monotonic() - elapsed_before_emergency

    emergency_active = False
    emergency_lane = None
    saved_signal_state = None

    return {
        "message": "Normal traffic signals restored",
        "restored_lane": saved_lane,
        "remaining_time": saved_remaining
    }