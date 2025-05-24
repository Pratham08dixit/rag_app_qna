import os
from uuid import uuid4
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.models import Document, Chunk
from db.database import get_db
from vectorstore.utils import UPLOAD_ROOT, rebuild_faiss_index
from langchain.text_splitter import RecursiveCharacterTextSplitter
from uuid import uuid4

router = APIRouter()

ALLOWED_EXT = {".pdf", ".txt", ".doc", ".docx"}
MAX_FILES       = 20
MAX_FILE_SIZEMB = 10

@router.post("/upload")
async def upload_files(
    request: Request,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # ensure session_id
    sid = request.session.get("session_id")
    if not sid:
        sid = str(uuid4())
        request.session["session_id"] = sid

    # initialize uploaded_files list
    session_files = request.session.get("uploaded_files", [])
    request.session["uploaded_files"] = session_files

    user_dir = os.path.join(UPLOAD_ROOT, sid)
    os.makedirs(user_dir, exist_ok=True)

    # enforce file count
    if len(files) + len(session_files) > MAX_FILES:
        raise HTTPException(400, f"Max {MAX_FILES} files allowed in session.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=20000, chunk_overlap=200)

    for uf in files:
        ext = os.path.splitext(uf.filename)[1].lower()
        content = await uf.read()
        size_mb = len(content) / (1024*1024)
        await uf.seek(0)

        if ext not in ALLOWED_EXT:
            continue
        if size_mb > MAX_FILE_SIZEMB:
            continue

        # save file
        dest = os.path.join(user_dir, uf.filename)
        with open(dest, "wb") as out_f:
            out_f.write(content)

        # record in session
        if uf.filename not in session_files:
            session_files.append(uf.filename)
        request.session["uploaded_files"] = session_files

        # DB: create Document record
        doc = Document(filename=uf.filename, session_id=sid)
        db.add(doc)
        db.flush()  # assign doc.id

        # chunk & store
        text = content.decode("utf-8", "ignore") if ext == ".txt" else None
        if ext == ".pdf" or ext in {".doc", ".docx"}:
            # let vectorstore rebuild pull from file rather than reuse text
            # but for metadata, count chunks via splitter applied to extracted text:
            from vectorstore.utils import rebuild_faiss_index  # reuse underlying code
            # Temporary hack: rebuild index first, then count
            vs = rebuild_faiss_index(sid)
            num = len(vs.index_to_docstore_id) if vs else 0
            doc.num_chunks = num
        else:
            chunks = splitter.split_text(text)
            doc.num_chunks = len(chunks)
            for c in chunks:
                db.add(Chunk(document_id=doc.id, content=c))

    db.commit()
    # rebuild FAISS index one final time
    rebuild_faiss_index(sid)
    return {"status": "uploaded", "uploaded_files": session_files}
