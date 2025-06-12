import os
import shutil
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, init_db, get_db
from main import app
import vectorstore.utils as vs_utils

# 1) Create an in‐memory SQLite engine & session factory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    # create tables once for the session
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    # each test gets a clean transaction
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture()
def client(tmp_path, db_session, monkeypatch):
    # 2) Override get_db to use our in‐memory session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db

    # 3) Point uploads & index dirs to tmp_path
    uploads_dir = tmp_path / "uploads"
    indices_dir = tmp_path / "faiss_indices"
    uploads_dir.mkdir()
    indices_dir.mkdir()
    monkeypatch.setattr(vs_utils, "UPLOAD_ROOT", str(uploads_dir))
    monkeypatch.setattr(vs_utils, "INDEX_PATH", str(indices_dir))

    # 4) Stub out embeddings to return dummy vectors
    class DummyEmbeddings:
        def __init__(self, model): pass
        def embed_documents(self, docs): return [[0.0] for _ in docs]
    monkeypatch.setattr("langchain_google_genai.embeddings.GoogleGenerativeAIEmbeddings", DummyEmbeddings)

    # 5) Stub out FAISS to skip real disk/indexing
    from langchain.schema import Document as LC_Document
    class DummyFAISS:
        @classmethod
        def from_documents(cls, docs, embed): return cls()
        def save_local(self, path): pass
        @classmethod
        def load_local(cls, path, embed, **kwargs): return cls()
        def similarity_search(self, query, k): 
            return [LC_Document(page_content="test chunk", metadata={})]
    monkeypatch.setattr("langchain.vectorstores.FAISS", DummyFAISS)

    # 6) Stub out chat model
    class DummyChat:
        def __init__(self, model): pass
        async def ainvoke(self, messages):
            class Msg: content = "dummy answer"
            return Msg()
    monkeypatch.setattr("langchain_google_genai.chat_models.ChatGoogleGenerativeAI", DummyChat)

    return TestClient(app)
