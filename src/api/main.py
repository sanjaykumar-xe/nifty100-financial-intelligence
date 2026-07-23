from time import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.database import get_table_counts
from src.api.routers import health
from src.api.routers import companies


app = FastAPI(
    title="Nifty100 Financial Intelligence API",
    description="API for accessing Nifty100 financial data.",
    version="1.0.0"
)


# Store application start time
app.state.start_time = time()


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def request_logger(request: Request, call_next):
    start = time()

    response = await call_next(request)

    duration = time() - start

    print(
        f"{request.method} {request.url.path} {duration:.4f}s"
    )

    return response


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to Nifty100 Financial Intelligence API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Include routers
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

app.include_router(
    companies.router,
    prefix="/api/v1",
    tags=["Companies"]
)