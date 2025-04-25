import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes import analyze, farming, autopilot, airdrop, credit, auth, feedback, chat, twitter
from core.database import Database
from routes.waitlist import router as waitlist_router

app = FastAPI(
    title="Scryptex API",
    description="Backend API for Scryptex Web3 project",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add startup event
@app.on_event("startup")
async def startup_event():
    await Database.connect()  # Gunakan Database.connect untuk menginisialisasi koneksi

# Add shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    await Database.disconnect()  # Gunakan Database.disconnect untuk menutup koneksi

# Include routers
app.include_router(analyze.router, prefix="/api", tags=["Analyzer"])
app.include_router(farming.router, prefix="/api", tags=["farming"])
app.include_router(autopilot.router, prefix="/api", tags=["autopilot"])
app.include_router(airdrop.router, prefix="/api", tags=["airdrop"])
app.include_router(credit.router, prefix="/api", tags=["credit"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(twitter.router, prefix="/api/twitter", tags=["twitter"])
app.include_router(waitlist_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Scryptex API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
