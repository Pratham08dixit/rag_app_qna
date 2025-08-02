# RAG Application - Document Q&A System

A production-ready Retrieval-Augmented Generation (RAG) pipeline that allows users to upload documents and ask questions based on their content. The system supports multiple LLM providers, features comprehensive testing, and is fully containerized for easy deployment.

## 🚀 Features

- **📄 Multi-Format Document Support**: PDF, TXT, DOC, DOCX with intelligent text extraction
- **🧠 LLM Providers**: Google Gemini
- **🔍 Advanced Vector Search**: FAISS-based similarity search with optimized chunking
- **⚡ High Performance**: Async processing, caching, and optimized retrieval
- **🌐 REST API**: Comprehensive FastAPI-based API documentation
- **🎨 Web Interface**: Modern, responsive UI for document upload and querying
- **🐳 Docker Ready**: Full containerization with Docker Compose support
- **🧪 Comprehensive Testing**: Unit, integration, and performance tests

## 📋 Requirements

- **Python**: 3.9 or higher
- **Storage**: 2GB+ free space for document storage and vector indices
- **Docker**: Optional, for containerized deployment

## 🚀 Quick Start


###  Local Development Setup

```bash
# 1. Clone and setup
git clone <repository-url>
cd rag_app

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Run the application
python main.py
```


### Docker Deployment

#### Using Docker

```bash
# Build the image
docker build -t rag-app .

# Run the container
docker run -p 8000:8000 --env-file .env rag-app
```

#### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Cloud Deployment

The application is ready for deployment on major cloud platforms:

#### AWS ECS/Fargate
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t rag-app .
docker tag rag-app:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-app:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-app:latest
```

## API Documentation

### Endpoints

#### Upload Documents
```http
POST /api/upload
Content-Type: multipart/form-data

files: [file1, file2, ...]
```

**Response:**
```json
{
  "status": "uploaded",
  "uploaded_files": ["document1.pdf", "document2.txt"]
}
```

#### Query Documents
```http
POST /api/query
Content-Type: application/json

{
  "question": "What is the main topic of the documents?"
}
```

**Response:**
```json
{
  "answer": "Based on the uploaded documents, the main topic is..."
}
```

#### Get Document Metadata
```http
GET /api/metadata
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "document1.pdf",
    "upload_time": "2024-01-01T12:00:00",
    "num_chunks": 25
  }
]
```

#### Delete Document
```http
DELETE /api/metadata/{doc_id}
```

**Response:**
```json
{
  "status": "removed",
  "filename": "document1.pdf"
}
```

## ⚙️ Configuration

### Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and configure:

```env
# =============================================================================
# CORE CONFIGURATION
# =============================================================================

# Application Settings
APP_NAME=RAG Application
APP_VERSION=1.0.0
ENVIRONMENT=development  # development, staging, production
DEBUG=true
PORT=8000
HOST=0.0.0.0

# Security
SESSION_SECRET=your_super_secret_session_key_change_in_production
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Database
DATABASE_URL=sqlite:///./rag.db
# For PostgreSQL: postgresql://user:password@localhost:5432/rag_db
# For MySQL: mysql://user:password@localhost:3306/rag_db

# =============================================================================
# LLM PROVIDER CONFIGURATION
# =============================================================================

# Primary LLM Provider
LLM_PROVIDER=google 

# Google Gemini Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-2.0-flash
GOOGLE_EMBEDDING_MODEL=models/embedding-001


# =============================================================================
# DOCUMENT PROCESSING CONFIGURATION
# =============================================================================

# File Upload Limits
MAX_FILES_PER_SESSION=20
MAX_FILE_SIZE_MB=10
MAX_PAGES_PER_FILE=1000
ALLOWED_FILE_TYPES=["pdf", "txt", "doc", "docx"]

# Text Chunking Configuration
CHUNK_SIZE=2000
CHUNK_OVERLAP=200
CHUNK_STRATEGY=recursive  # recursive, semantic, fixed

# Vector Store Configuration
VECTOR_STORE_TYPE=faiss  # faiss, pinecone, weaviate, chroma
VECTOR_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7
MAX_RETRIEVAL_RESULTS=5

# =============================================================================
# PERFORMANCE & CACHING
# =============================================================================

# Caching
ENABLE_CACHING=true
CACHE_TTL_SECONDS=3600
CACHE_TYPE=memory  # memory, redis
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10

# =============================================================================
# MONITORING & LOGGING
# =============================================================================

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json  # json, text
LOG_FILE=logs/app.log


#### Provider Fallback Chain


## File Format Support

| Format | Extension | Max Pages | Notes |
|--------|-----------|-----------|-------|
| PDF | .pdf | 1000 | Full text extraction |
| Text | .txt | N/A | UTF-8 encoding |
| Word | .doc, .docx | 1000 | Paragraph-based extraction |

## Limitations

- Maximum 20 documents per session
- Maximum 1000 pages per document
- Maximum 10MB per file
- Session-based storage (not persistent across server restarts)

## 🧪 Testing

Comprehensive test suite with unit, integration, and performance tests.

### Test Categories

| Test Type | Coverage | Purpose |
|-----------|----------|----------|
| **Unit Tests** | Individual functions/classes | Fast feedback, isolated testing |
| **Integration Tests** | Full RAG pipeline | End-to-end functionality |
| **Performance Tests** | Load and stress testing | Performance benchmarks |
| **Security Tests** | Input validation, auth | Security compliance |

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-xdist

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term

# Run specific test categories
pytest tests/test_upload.py -v                    # Unit tests
pytest tests/test_integration.py -v               # Integration tests
pytest tests/test_performance.py -v               # Performance tests
pytest tests/test_performance.py -v -m "not slow" # Quick performance tests

# Run tests in parallel
pytest -n auto

# Run with specific markers
pytest -m "unit"                    # Only unit tests
pytest -m "integration"             # Only integration tests
pytest -m "not slow"                # Exclude slow tests
```

### Test Configuration

```bash
# pytest.ini configuration
[tool:pytest]
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Generate XML coverage for CI
pytest --cov=. --cov-report=xml

# Coverage with branch analysis
pytest --cov=. --cov-branch --cov-report=term-missing
```

### Test Environment Setup

```bash
# Create test environment file
cp .env.example .env.test

# Edit .env.test with test-specific values
GOOGLE_API_KEY=test_key_or_real_key_for_integration_tests
DATABASE_URL=sqlite:///:memory:
ENVIRONMENT=test
DEBUG=false

# Run tests with test environment
pytest --envfile=.env.test
```

### Integration Test Examples

```python
# Test full RAG pipeline
def test_full_rag_pipeline(client):
    # Upload document
    response = client.post("/api/upload", files={"files": ("test.txt", b"content")})
    assert response.status_code == 200

    # Query document
    response = client.post("/api/query", json={"question": "What is this about?"})
    assert response.status_code == 200
    assert "answer" in response.json()

# Test multiple LLM providers
def test_llm_provider_fallback(client):
    # Test with primary provider
    # Test fallback when primary fails
    # Verify response quality
```

### Performance Benchmarks

| Metric | Target | Measurement |
|--------|--------|--------------|
| **Upload Time** | <30s for 10 files | Average processing time |
| **Query Response** | <5s average | 95th percentile response time |
| **Concurrent Users** | 50+ simultaneous | Load testing results |
| **Memory Usage** | <2GB for 100 docs | Peak memory consumption |




