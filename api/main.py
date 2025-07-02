from dotenv import load_dotenv
# Pastikan ini adalah dua baris paling pertama di file Anda
# untuk memuat environment variables sebelum modul lain diimpor.
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze
import os

app = FastAPI(
    title="Rainative AI API",
    description="AI-powered content analysis and viral prediction API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
# Daftar origins ini di-hardcode, sesuai dengan kode asli Anda.
# Jika Anda ingin membuatnya dinamis dari .env, perlu ada perubahan lebih lanjut.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174", # Port dari error CORS sebelumnya
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze.router, prefix="/api", tags=["analyze"])

@app.get("/")
async def root():
    return {
        "message": "Rainative AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Rainative AI API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )