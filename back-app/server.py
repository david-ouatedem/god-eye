from fastapi import FastAPI, Request
from typing import List
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Store latest data to serve via GET request
latest_traffic_data = []

app = FastAPI()

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Adjust the allowed origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GET endpoint to retrieve traffic data
@app.get("/traffic-data")
async def get_traffic_data():
    return {"traffic_data": latest_traffic_data}

# POST endpoint to update traffic data
@app.post("/traffic-data")
async def post_traffic_data(data: List[dict]):
    global latest_traffic_data
    latest_traffic_data = data  # Update the latest traffic data
    return {"status": "Data received"}

# Start FastAPI server if this file is run directly
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8081)
