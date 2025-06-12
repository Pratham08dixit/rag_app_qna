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
from routes.chat import router as chat_router

# Load environment variables
load_dotenv()

# Configure Google API
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print(f"✅ Google API configured with key: {os.getenv('GOOGLE_API_KEY')[:10]}...")
print(f"✅ Environment: {os.getenv('ENVIRONMENT', 'development')}")
print(f"✅ Port: {os.getenv('PORT', '8000')}")
print(f"✅ Google Model: {os.getenv('GOOGLE_MODEL', 'gemini-2.0-flash')}")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "change_me"))

# Initialize database & uploads folder
@app.on_event("startup")
def on_startup():
    init_db()
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("faiss_indices", exist_ok=True)

templates = Jinja2Templates(directory="templates")

# Mount changes
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(query_router,  prefix="/api", tags=["query"])
app.include_router(meta_router,   prefix="/api", tags=["metadata"])
app.include_router(chat_router,   prefix="/api", tags=["chat"])

# Preserve existing frontend
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not request.session.get("session_id"):
        request.session["session_id"] = str(uuid4())
    request.session.setdefault("uploaded_files", [])
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
