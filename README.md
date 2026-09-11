# SN5 Telemetry Site

A web application for uploading and visualizing CSV telemetry data logged from the SN5 racecar's CAN bus, with automatic detection of statistically significant data points.

## Features

- Upload CSV telemetry logs and store them for later review
- Browse past uploads (runs) and view any signal within a run as a chart
- View summary statistics (min/max/mean/std) for any signal
- Automatic anomaly detection: flags data points that deviate significantly from a signal's typical behavior (z-score based)

## Tech Stack

- **Frontend:** SvelteKit (TypeScript) + Chart.js
- **Backend:** FastAPI (Python) + pandas
- **Database:** SQLite
## Setup

### Backend

```bash
cd back_end
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 database.py            # creates telemetry.db (one-time)
uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000`. Interactive API docs at `http://127.0.0.1:8000/docs`.

### Frontend

In a separate terminal:

```bash
cd front_end
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

**Both servers need to be running at the same time** for the app to work — the frontend is a static UI that fetches everything from the backend over HTTP.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Server status check |
| POST | `/upload` | Upload a CSV, parse it, and store it |
| GET | `/runs` | List all uploaded runs |
| GET | `/runs/{run_id}/signals` | List available signal names for a run |
| GET | `/runs/{run_id}/signals?signal_name=X` | Get time-series data for one signal |
| GET | `/runs/{run_id}/signals/{signal_name}/stats` | Min/max/mean/std for one signal |
| GET | `/runs/{run_id}/signals/{signal_name}/anomalies` | Data points beyond N std devs from the mean |

## Known Limitations

- No de-duplication check on upload — uploading the same file twice creates two separate runs.