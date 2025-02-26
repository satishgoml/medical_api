from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from typing import AsyncGenerator, List
import json
import asyncio
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Import workflow components
import sys
sys.path.append("")
from src.graph import medical_workflow
from src.schema import Plan, Task

# Set up Jinja2 templates directory

app = FastAPI(title="Medical Workflow API")

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow localhost:3000
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Define data directory path
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

class MedicalQuery(BaseModel):
    input: str

def serialize_event(event_data):
    """Serialize event data to JSON string using default JSON encoder"""
    return json.dumps(event_data, default=lambda obj: obj.model_dump() if isinstance(obj, (Plan, Task)) else str(obj))

async def event_generator(workflow_input: dict) -> AsyncGenerator[str, None]:
    """Generate SSE events from workflow execution."""
    try:
        config = {"recursion_limit": 50}
        
        async for event in medical_workflow.astream(workflow_input, config=config):
            for k, v in event.items():
                # if (k == "__end__"):
                #     # Send final event
                #     yield f"data: {serialize_event({'event': 'end', 'data': 'Workflow completed'})}\n\n"

                event_data = {
                    'event': k,
                    'data': v  # Keep as object for custom serialization
                }
                
                yield f"data: {serialize_event(event_data)}\n\n"
                
                # Small delay to ensure events are properly separated
                await asyncio.sleep(0.01)


        yield f"data: {serialize_event({'event': 'end', 'data': 'Workflow completed'})}\n\n"

    except Exception as e:
        yield f"data: {serialize_event({'event': 'error', 'data': str(e)})}\n\n"

# POST endpoint
@app.post("/medical/diagnose")
async def diagnose_post(query: MedicalQuery):
    """
    Start a medical diagnosis workflow with SSE streaming response (POST)
    """
    return StreamingResponse(
        event_generator({"input": query.input}),
        media_type="text/event-stream"
    )

# GET endpoint
@app.get("/medical/diagnose")
async def diagnose_get(input: str):
    """
    Start a medical diagnosis workflow with SSE streaming response (GET)
    """
    return StreamingResponse(
        event_generator({"input": input}),
        media_type="text/event-stream"
    )

# File handling endpoints
@app.get("/files/list")
async def list_files() -> List[str]:
    """
    List all files in the data directory
    """
    try:
        files = os.listdir(DATA_DIR)
        return files
    except Exception as e:
        return {"error": str(e)}

@app.get("/files/{filename}")
async def get_file(filename: str):
    """
    Download a specific file from the data directory
    """
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(
        path=file_path, 
        filename=filename,
        media_type="application/octet-stream"
    )

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the data directory
    """
    try:
        # Ensure the data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        file_path = os.path.join(DATA_DIR, file.filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {"filename": file.filename, "status": "File uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
