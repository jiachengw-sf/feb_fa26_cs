from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import UploadFile, File

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

    return {"filename": file.filename, "size_bytes": len(contents)}