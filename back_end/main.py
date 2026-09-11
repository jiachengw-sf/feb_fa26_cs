from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import UploadFile, File
import pandas as pd
import sqlite3
from database import DB
from fastapi import Query
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "backend is running"}

UPLOAD = "uploads"
os.makedirs(UPLOAD, exist_ok=True)

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD, file.filename)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    df = pd.read_csv(file_path)
    df.rename(columns={"timestamp": "timestamp_ms", "name": "signal_name"}, inplace=True)

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO runs (filename, uploaded_at) VALUES (?, datetime('now'))",
        (file.filename,)
    )
    run_id = cursor.lastrowid

    df["run_id"] = run_id
    df.to_sql("signals", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    return {"filename": file.filename, "run_id": run_id, "rows_inserted": len(df)}

@app.get("/runs")
def get_runs():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, uploaded_at FROM runs")
    rows = cursor.fetchall()
    conn.close()

    return [
        {"id": row[0], "filename": row[1], "uploaded_at": row[2]}
        for row in rows
    ]

@app.get("/runs/{run_id}/signals")
def get_signals(run_id: int, signal_name:  Optional[str] = Query(None)):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    if signal_name:
        cursor.execute(
            "SELECT timestamp_ms, value, physical_value FROM signals WHERE run_id = ? AND signal_name = ? ORDER BY timestamp_ms",
            (run_id, signal_name)
        )
    else:
        cursor.execute(
            "SELECT DISTINCT signal_name FROM signals WHERE run_id = ?",
            (run_id,)
        )

    rows = cursor.fetchall()
    conn.close()

    if signal_name:
        return [
            {"timestamp_ms": row[0], "value": row[1], "physical_value": row[2]}
            for row in rows
        ]
    else:
        return {"available_signals": [row[0] for row in rows]}

@app.get("/runs/{run_id}/signals/{signal_name}/stats")
def get_signal_stats(run_id: int, signal_name: str):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT value FROM signals WHERE run_id = ? AND signal_name = ?",
        (run_id, signal_name)
    )
    rows = cursor.fetchall()
    conn.close()

    values = [row[0] for row in rows if row[0] is not None]

    if not values:
        return {"error": "No data found for this signal"}

    series = pd.Series(values)

    return {
        "signal_name": signal_name,
        "count": len(series),
        "min": series.min(),
        "max": series.max(),
        "mean": round(series.mean(), 3),
        "std": round(series.std(), 3)
    }

@app.get("/runs/{run_id}/signals/{signal_name}/anomalies")
def get_anomalies(run_id: int, signal_name: str, threshold: float = 2.0):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp_ms, value FROM signals WHERE run_id = ? AND signal_name = ? ORDER BY timestamp_ms",
        (run_id, signal_name)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"error": f"No data found for signal '{signal_name}' in this run"}

    df = pd.DataFrame(rows, columns=["timestamp_ms", "value"])
    df = df.dropna(subset=["value"])

    if df.empty:
        return {"error": f"No numeric data found for signal '{signal_name}'"}

    mean = df["value"].mean()
    std = df["value"].std()

    if pd.isna(std) or std == 0:
        return {"anomalies": [], "note": "Not enough variation in this signal to detect anomalies"}

    df["z_score"] = (df["value"] - mean) / std
    anomalies = df[df["z_score"].abs() > threshold]

    return {
        "signal_name": signal_name,
        "mean": round(mean, 3),
        "std": round(std, 3),
        "threshold": threshold,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies[["timestamp_ms", "value"]].to_dict(orient="records")
    }
