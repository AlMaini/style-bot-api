import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, health, images, payments, status, try_on

_ = load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # delete images in app/images on shutdown
    folder_path = "app/images"
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".png"):
                file_path = os.path.join(folder_path, filename)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {filename}")
                except OSError as e:
                    print(f"Error deleting {filename}: {e}")


app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        FRONTEND_URL,
    ],  # add frontend URLS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(try_on.router)
app.include_router(status.router)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(payments.router)
app.include_router(images.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
