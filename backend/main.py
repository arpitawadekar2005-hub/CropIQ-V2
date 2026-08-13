from fastapi import FastAPI

app = FastAPI(title="CropIQ API")


@app.get("/")
def home():
    return {
        "project": "CropIQ",
        "message": "CropIQ backend is running"
    }


@app.get("/test")
def test():
    return {
        "status": "success",
        "message": "Backend connection is working"
    }
