import os
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from db.models import Document
from db.database import get_db
from vectorstore.utils import UPLOAD_ROOT, rebuild_faiss_index

router = APIRouter()

@router.get("/metadata")
def list_documents(
    request: Request,
    db: Session = Depends(get_db)
):
    sid = request.session.get("session_id")
    if not sid:
        return []
    docs = db.query(Document).filter_by(session_id=sid).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "upload_time": d.upload_time,
            "num_chunks": d.num_chunks
        }
        for d in docs
    ]

@router.delete("/metadata/{doc_id}")
def remove_document(
    request: Request,
    doc_id: int,
    db: Session = Depends(get_db)
):
    sid = request.session.get("session_id")
    doc = db.query(Document).filter_by(id=doc_id, session_id=sid).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    # delete file
    path = os.path.join(UPLOAD_ROOT, sid, doc.filename)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

    # delete DB records
    db.delete(doc)
    db.commit()

    # rebuild index
    rebuild_faiss_index(sid)
    return {"status": "removed", "filename": doc.filename}
