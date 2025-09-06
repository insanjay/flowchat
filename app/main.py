from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import messages, search
from app.database.connection import create_tables
from fastapi.responses import FileResponse
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Advanced Messaging App", version="0.1.0")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Include routers
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

@app.on_event("startup")  # FIX: Proper database initialization
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "Messaging App API"}

@app.get("/chat")
async def get_chat_interface():
    return templates.TemplateResponse("index.html", {"request": {}})

# WebSocket for real-time messaging
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Real-time message handling

@app.get("/files/{filename}")
async def download_file(filename: str):
    file_path = f"files/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return {"error": "File not found"}

# Add these imports at the top
# Add this after app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://insanjay.github.io"],
    allow_methods=["*"],
    allow_headers=["*"],
)
