# SirenSync – AI-Based Intelligent Emergency Traffic Management System

## 1. Introduction

SirenSync is an AI-based emergency traffic management system designed to detect approaching ambulances using computer vision and audio analysis.

The system identifies the ambulance's estimated approach lane and gives that lane priority through a simulated traffic signal system. It also monitors traffic density and displays emergency alerts on a web dashboard.

## 2. Key Features

- AI-based ambulance detection using YOLO.
- Camera-based vehicle monitoring.
- Estimated lane identification.
- Traffic density monitoring.
- Emergency signal priority.
- Restoration of the previous signal state after an emergency.
- Live traffic dashboard.
- Emergency event history.
- CSV report download.
- Experimental siren audio analysis.

## 3. Technologies Used

**Backend**
- Python
- FastAPI
- Uvicorn

**Artificial Intelligence**
- YOLO
- Ultralytics
- OpenCV
- NumPy

**Audio Processing**
- SoundDevice
- NumPy FFT

**Frontend**
- HTML
- CSS
- JavaScript

**Development Tools**
- Visual Studio Code
- Git
- GitHub

## 4. Project Structure

```text
SirenSync/
│
├── ai_engine/
│   ├── vision/
│   ├── audio/
│   └── models/
│
├── backend/
│   ├── database/
│   ├── middleware/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── main.py
│
├── datasets/
│   └── ambulance_dataset/
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   └── js/
│   └── templates/
│
├── logs/
├── runs/
├── tests/
├── uploads/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 5. Installation

Clone the repository:

```bash
git clone https://github.com/Akshatha722/SirenSync.git
```

Open the project directory:

```bash
cd SirenSync
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## 6. Running the Project

Start the FastAPI backend from the project root:

```powershell
python -m uvicorn backend.main:app --reload
```

Open the application in a browser:

```text
http://127.0.0.1:8000
```

Open the dashboard:

```text
http://127.0.0.1:8000/dashboard
```

## 7. Running the AI Camera Monitor

With the backend running, open another terminal, activate the virtual environment and run:

```powershell
python .\ai_engine\vision\camera_monitor.py
```

Press `Q` to close the camera window.

## 8. Project Safety

SirenSync is an academic prototype intended for simulation and demonstration.

It must not be connected to or control real public-road traffic signals. Any hardware demonstration should use a safe, low-voltage model.

## 9. Current Development Status

The project is under active development. Some components, including audio-based siren detection and lane estimation, are experimental and require further testing.