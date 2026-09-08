from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import UploadFile, File
import pandas as pd
import sqlite3
from database import DB

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