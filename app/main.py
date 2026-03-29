from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers.jobs import router as jobs_router
from app.routers.auth import router as auth_router
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.db_processor import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown events"""

    # get the db object from connect to mongo
    db_client =  await connect_to_mongo(app)

    # store it in the app.state 
    # app.state.db_client = client
    
    
    yield
    # Shutdown
    await close_mongo_connection(app)

app = FastAPI(
    title="Job Tracker API",
    description="API for tracking job applications",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # Allow local development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(jobs_router, prefix="/api/v1", tags=["jobs"])

@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse("templates/index.html", media_type="text/html")





