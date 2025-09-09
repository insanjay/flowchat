from app.api.routes.users import router as users_router
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import messages, search
from app.database.connection import create_tables
from fastapi.responses import FileResponse
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code - runs before app starts serving requests
    print("Starting up: initializing database, etc.")
    create_tables()  # Initialize your database tables
    
    yield  # App runs here
    templates = Jinja2Templates(directory="./frontend/templates")
    # Shutdown code - runs after app stops serving requests
    print("Shutting down: cleaning up resources")
    # Close database connections, cleanup, etc.

app = FastAPI(title="Advanced Messaging App", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://insanjay.github.io"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_credentials=True,
)

# Mount static files
app.mount("/frontend/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="./")

# Include routers
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(users_router)  # Add this line after your existing routers

@app.get("/")
async def root():
    return {"message": "Backend is running"}

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

templates = Jinja2Templates(directory="frontend/templates")

@app.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})