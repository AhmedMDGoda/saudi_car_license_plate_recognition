import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from typing import List
from ALPR import car_plate

app = FastAPI()

@app.get("/")
async def route():
    return {"message": "Saudi License Plate Recognition System"}

@app.post("/analyze/")
async def analyze_route(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        contents = await file.read()
        nparr = np.fromstring(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        texts = car_plate(img,file.filename)
        results.append(texts)
    return {"results": results}
    
    
    