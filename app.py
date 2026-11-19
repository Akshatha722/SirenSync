from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

lanes = ["North", "South", "East", "West"]
# Adaptive traffic signal timings
MIN_GREEN_TIME = 15
NORMAL_GREEN_TIME = 30
MAX_GREEN_TIME = 45

lane_durations = {
    "North": 30,
    "South": 30,
    "East": 30,
    "West": 30
}

start_time = time.monotonic()

emergency_active = False
emergency_lane = None
# Traffic density information
traffic_counts = {
    "North": 0,
    "South": 0,
    "East": 0,
    "West": 0
}
saved_signal_state = None
LOG_FILE = "logs/emergency_events.csv"


class EmergencyRequest(BaseModel):
    lane: str
class TrafficCountRequest(BaseModel):
    lane: str
    count: int
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

    # Total duration of one complete signal cycle
    cycle_duration = sum(lane_durations.values())

    # Current position in the signal cycle
    cycle_position = elapsed % cycle_duration

    # Identify the active lane
    for lane in lanes:

        duration = lane_durations[lane]

        if cycle_position < duration:

            remaining = duration - cycle_position

            return lane, remaining

        cycle_position -= duration

    return lanes[0], lane_durations[lanes[0]]


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={}
    )


@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.post("/api/traffic/count")
def update_traffic_count(data: TrafficCountRequest):

    if data.lane not in lanes:
        return {"error": "Invalid lane"}

    if data.count < 0:
        return {"error": "Invalid vehicle count"}

    traffic_counts[data.lane] = data.count
        # Assign green signal duration based on traffic density
    if data.count <= 2:
        density = "LOW"
        if not emergency_active:
            lane_durations[data.lane] = MIN_GREEN_TIME

    elif data.count <= 5:
        density = "MEDIUM"
        if not emergency_active:
            lane_durations[data.lane] = NORMAL_GREEN_TIME

    else:
        density = "HIGH"
        if not emergency_active:
            lane_durations[data.lane] = MAX_GREEN_TIME

    

    return {
        "lane": data.lane,
        "vehicle_count": data.count,
        "traffic_density": density,
        "green_duration": lane_durations[data.lane]
    }
@app.get("/api/status")
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

    traffic_density = {}

    for lane, count in traffic_counts.items():

        if count <= 2:
            traffic_density[lane] = "LOW"

        elif count <= 5:
            traffic_density[lane] = "MEDIUM"

        else:
            traffic_density[lane] = "HIGH"

    return {
        "system": "Online",
        "ambulance_detected": emergency_active,
        "emergency_active": emergency_active,
        "traffic_signal": "GREEN",
        "current_lane": current_lane,
        "remaining_time": remaining,
        "lane_signals": lane_signals,
        "traffic_counts": traffic_counts,
        "traffic_density": traffic_density
    }
@app.get("/api/emergency/history")
def emergency_history():
    if not os.path.exists(LOG_FILE):
        return {"events": []}

    with open(LOG_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        events = list(reader)

    events.reverse()

    return {"events": events}

@app.get("/api/emergency/download")
def download_emergency_report():

    if not os.path.exists(LOG_FILE):
        return {"message": "No emergency records available"}

    return FileResponse(
        path=LOG_FILE,
        filename="SirenSync_Emergency_Report.csv",
        media_type="text/csv"
    )

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
    phase_start_offset = sum(
        lane_durations[lane] for lane in lanes[:lanes.index(saved_lane)]
    )

    elapsed_in_saved_lane = (
        lane_durations[saved_lane] - saved_remaining
    )

    elapsed_before_emergency = (
        phase_start_offset + elapsed_in_saved_lane
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