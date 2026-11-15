from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

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


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


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