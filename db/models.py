from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id           = Column(Integer, primary_key=True, index=True)
    filename     = Column(String, nullable=False)
    session_id   = Column(String, index=True, nullable=False)
    upload_time  = Column(DateTime, default=datetime.utcnow)
    num_chunks   = Column(Integer, default=0)

    chunks       = relationship("Chunk", back_populates="document", cascade="all, delete")

class Chunk(Base):
    __tablename__ = "chunks"
    id           = Column(Integer, primary_key=True, index=True)
    document_id  = Column(Integer, ForeignKey("documents.id"))
    content      = Column(Text, nullable=False)

    document     = relationship("Document", back_populates="chunks")

class QueryLog(Base):
    __tablename__ = "query_logs"
    id           = Column(Integer, primary_key=True, index=True)
    session_id   = Column(String, index=True)
    question     = Column(Text, nullable=False)
    response     = Column(Text, nullable=False)
    timestamp    = Column(DateTime, default=datetime.utcnow)
