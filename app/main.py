from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
import time

from .database import engine
from .models import Base
from .routes import auth, resumes, portfolios, payments

# Initialize logger
logger.add("logs/app.log", rotation="10 MB")

from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Appify Core Engine", 
    version="1.0.0",
    docs_url=None,   # 🔒 Disable Swagger UI
    redoc_url=None,  # 🔒 Disable Redoc
    openapi_url=None # 🔒 Disable OpenAPI Schema
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Completed {request.method} {request.url} - Status: {response.status_code} in {process_time:.4f}s")
        return response
    except Exception as exc:
        logger.error(f"Failed {request.method} {request.url} - Error: {exc}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error. Our engineers are on it."})

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(portfolios.router)
app.include_router(payments.router)

@app.get("/health")
def health():
    logger.info("Health check ping")
    return {"status": "Backend healthy 💚"}