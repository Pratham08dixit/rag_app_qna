import os
from fastapi import APIRouter, HTTPException, Depends, Request, Body
from sqlalchemy.orm import Session
from db.models import QueryLog
from db.database import get_db
from vectorstore.utils import INDEX_PATH
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

router = APIRouter()

@router.post("/query")
async def query_docs(
    request: Request,
    question: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Query documents using RAG pipeline with Gemini"""
    sid = request.session.get("session_id")
    if not sid:
        raise HTTPException(400, "No active session.")

    if not question.strip():
        raise HTTPException(400, "Question cannot be empty.")

    try:
        # Load FAISS vector store
        embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        try:
            vs = FAISS.load_local(INDEX_PATH, embedding, allow_dangerous_deserialization=True)
        except Exception as e:
            raise HTTPException(500, "Vector store not initialized. Please upload documents first.")

        # Retrieve relevant documents
        max_results = int(os.getenv("MAX_RETRIEVAL_RESULTS", "5"))
        docs = vs.similarity_search(question, k=max_results)

        if not docs:
            answer = "I couldn't find any relevant information in the uploaded documents to answer your question."
            sources_count = 0
        else:
            # Prepare context from retrieved documents
            context_parts = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                context_parts.append(f"[Document {i} - {source}]\n{doc.page_content}")

            context = "\n\n".join(context_parts)

            # Enhanced system prompt
            system_prompt = (
                "You are a helpful AI assistant that answers questions based on the provided context. "
                "Follow these guidelines:\n"
                "1. Answer only based on the information provided in the context\n"
                "2. If the answer is not available in the context, clearly state that\n"
                "3. Be concise but comprehensive in your response\n"
                "4. If you reference specific information, mention which document it came from\n"
                "5. Maintain a professional and helpful tone"
            )

            # Generate response using Gemini
            llm = ChatGoogleGenerativeAI(
                model=os.getenv("GOOGLE_MODEL", "gemini-2.0-flash"),
                temperature=0.1
            )

            ai_msg = await llm.ainvoke([
                ("system", system_prompt),
                ("human", f"Context:\n{context}\n\nQuestion: {question}")
            ])
            answer = ai_msg.content
            sources_count = len(docs)

        # Log query and response to database
        try:
            log = QueryLog(session_id=sid, question=question, response=answer)
            db.add(log)
            db.commit()
        except Exception as e:
            # Don't fail the request if logging fails
            pass

        return {
            "answer": answer,
            "sources_count": sources_count,
            "session_id": sid
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(500, f"An error occurred while processing your query: {str(e)}")
