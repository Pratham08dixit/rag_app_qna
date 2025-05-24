import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from uuid import uuid4
from db.database import init_db
from routes.upload import router as upload_router
from routes.query  import router as query_router
from routes.metadata import router as meta_router

load_dotenv()
# configure Google API
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "change_me"))

# Initialize database & uploads folder
@app.on_event("startup")
def on_startup():
    init_db()
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("faiss_indices", exist_ok=True)

templates = Jinja2Templates(directory="templates")

# Mount 
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(query_router,  prefix="/api", tags=["query"])
app.include_router(meta_router,   prefix="/api", tags=["metadata"])

# Preserve existing frontend flow
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not request.session.get("session_id"):
        request.session["session_id"] = str(uuid4())
    request.session.setdefault("uploaded_files", [])
    return templates.TemplateResponse("index.html", {"request": request})
