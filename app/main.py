from fastapi import FastAPI

app = FastAPI(
    title="Bookify API",
    description="Production-ready service booking platform",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Bookify API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
