from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CodexQuery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # we'll lock this down to your Vercel domain before deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "CodexQuery API is running"}