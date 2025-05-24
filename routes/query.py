from fastapi import APIRouter, HTTPException, Depends, Request, Body
from sqlalchemy.orm import Session
from db.models import QueryLog
from db.database import get_db
from vectorstore.utils import INDEX_PATH
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
import google.generativeai as genai
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

router = APIRouter()

@router.post("/query")
async def query_docs(
    request: Request,
    question: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    sid = request.session.get("session_id")
    if not sid:
        raise HTTPException(400, "No active session.")

    # load FAISS
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    try:
        vs = FAISS.load_local(INDEX_PATH, embedding, allow_dangerous_deserialization=True)
    except:
        raise HTTPException(500, "Vector store not initialized.")

    docs = vs.similarity_search(question, k=5)
    context = "\n\n".join(d.page_content for d in docs)

    system_prompt = (
        "Answer based on context; if unavailable, reply 'answer is not available in the context'."
    )
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    ai_msg = await llm.ainvoke([
        ("system", system_prompt),
        ("human", f"Context:\n{context}\n\nQuestion: {question}")
    ])
    answer = ai_msg.content

    # log to DB
    log = QueryLog(session_id=sid, question=question, response=answer)
    db.add(log)
    db.commit()

    return {"answer": answer}
