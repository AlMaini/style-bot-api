from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    image_generation,
    virtual_tryon,
    clothing_analysis,
    health,
    auth,
    supabase,
    accessories,
    outfits,
    clothing,
)

# Initialize FastAPI app
app = FastAPI(
    title="Drip Drop Image Generator",
    description="Generate images using Gemini AI with context images",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(supabase.router)
app.include_router(image_generation.router)
app.include_router(virtual_tryon.router)
app.include_router(clothing_analysis.router)
app.include_router(clothing.router, prefix="/api/v1", tags=["clothing"])
app.include_router(accessories.router, prefix="/api/v1", tags=["accessories"])
app.include_router(outfits.router, prefix="/api/v1", tags=["outfits"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
