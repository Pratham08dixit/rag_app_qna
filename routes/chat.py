"""
Chat history management routes
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from db.models import QueryLog
from db.database import get_db
from typing import List, Dict, Any
import json

router = APIRouter()

@router.get("/chat-history")
async def get_chat_history(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get chat history for the current session"""
    sid = request.session.get("session_id")
    if not sid:
        return []
    
    try:
        # Get all queries for this session
        queries = db.query(QueryLog).filter(
            QueryLog.session_id == sid
        ).order_by(QueryLog.timestamp).all()
        
        chat_history = []
        for query in queries:
            chat_history.append({
                "id": query.id,
                "question": query.question,
                "answer": query.response,
                "timestamp": query.timestamp.isoformat(),
                "session_id": query.session_id
            })
        
        return chat_history
        
    except Exception as e:
        raise HTTPException(500, f"Error retrieving chat history: {str(e)}")


@router.delete("/chat-history")
async def clear_chat_history(
    request: Request,
    db: Session = Depends(get_db)
):
    """Clear chat history for the current session"""
    sid = request.session.get("session_id")
    if not sid:
        raise HTTPException(400, "No active session.")
    
    try:
        # Delete all queries for this session
        deleted_count = db.query(QueryLog).filter(
            QueryLog.session_id == sid
        ).delete()
        
        db.commit()
        
        return {
            "message": f"Cleared {deleted_count} chat messages",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error clearing chat history: {str(e)}")


@router.get("/chat-history/export")
async def export_chat_history(
    request: Request,
    db: Session = Depends(get_db)
):
    """Export chat history as text"""
    sid = request.session.get("session_id")
    if not sid:
        raise HTTPException(400, "No active session.")
    
    try:
        # Get all queries for this session
        queries = db.query(QueryLog).filter(
            QueryLog.session_id == sid
        ).order_by(QueryLog.timestamp).all()
        
        if not queries:
            raise HTTPException(404, "No chat history found")
        
        # Format as text
        content_lines = []
        content_lines.append("RAG Assistant - Chat History Export")
        content_lines.append("=" * 50)
        content_lines.append(f"Session ID: {sid}")
        content_lines.append(f"Total Messages: {len(queries)}")
        content_lines.append("")
        
        for i, query in enumerate(queries, 1):
            content_lines.append(f"Message {i}")
            content_lines.append(f"Timestamp: {query.timestamp}")
            content_lines.append(f"Question: {query.question}")
            content_lines.append(f"Answer: {query.response}")
            content_lines.append("-" * 30)
            content_lines.append("")
        
        content = "\n".join(content_lines)
        
        return {
            "content": content,
            "filename": f"chat-history-{sid[:8]}.txt",
            "message_count": len(queries)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error exporting chat history: {str(e)}")


@router.get("/stats")
async def get_session_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get session statistics"""
    sid = request.session.get("session_id")
    if not sid:
        return {
            "total_questions": 0,
            "total_documents": 0,
            "session_id": None,
            "session_active": False
        }
    
    try:
        # Count queries
        query_count = db.query(QueryLog).filter(
            QueryLog.session_id == sid
        ).count()
        
        # Count documents (this would need to be implemented in metadata route)
        # For now, we'll return 0 and let the frontend handle it
        
        return {
            "total_questions": query_count,
            "total_documents": 0,  # Will be updated by frontend
            "session_id": sid,
            "session_active": True
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error retrieving session stats: {str(e)}")
