# RAG Application - Document Q&A System

[![CI/CD Pipeline](https://github.com/your-repo/rag-app/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/your-repo/rag-app/actions)
[![Coverage](https://codecov.io/gh/your-repo/rag-app/branch/main/graph/badge.svg)](https://codecov.io/gh/your-repo/rag-app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A production-ready Retrieval-Augmented Generation (RAG) pipeline that allows users to upload documents and ask questions based on their content. The system supports multiple LLM providers, features comprehensive testing, and is fully containerized for easy deployment.

## 🚀 Features

- **📄 Multi-Format Document Support**: PDF, TXT, DOC, DOCX with intelligent text extraction
- **🧠 Multiple LLM Providers**: Google Gemini, OpenAI GPT, Anthropic Claude, and more
- **🔍 Advanced Vector Search**: FAISS-based similarity search with optimized chunking
- **⚡ High Performance**: Async processing, caching, and optimized retrieval
- **🔒 Session Management**: Secure user session-based document isolation
- **🌐 REST API**: Comprehensive FastAPI-based API with OpenAPI documentation
- **🎨 Web Interface**: Modern, responsive UI for document upload and querying
- **🐳 Docker Ready**: Full containerization with Docker Compose support
- **🧪 Comprehensive Testing**: Unit, integration, and performance tests
- **📊 Monitoring**: Built-in health checks and optional Prometheus/Grafana integration

## 📋 Requirements

- **Python**: 3.9 or higher
- **Memory**: Minimum 4GB RAM (8GB+ recommended for large documents)
- **Storage**: 2GB+ free space for document storage and vector indices
- **API Keys**: At least one LLM provider API key (Google, OpenAI, or Anthropic)
- **Docker**: Optional, for containerized deployment

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd rag_app

# 2. Configure environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section)

# 3. Start all services
docker-compose up -d

# 4. Access the application
# Web Interface: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Option 2: Local Development Setup

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

### Option 3: Production Deployment

```bash
# With reverse proxy and monitoring
docker-compose --profile production up -d

# With monitoring only
docker-compose --profile monitoring up -d
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

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/rag-app
gcloud run deploy --image gcr.io/PROJECT-ID/rag-app --platform managed
```

#### Azure Container Instances
```bash
# Build and push to ACR
az acr build --registry <registry-name> --image rag-app .
az container create --resource-group <resource-group> --name rag-app --image <registry-name>.azurecr.io/rag-app:latest
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

# Primary LLM Provider (choose one)
LLM_PROVIDER=google  # google, openai, anthropic, azure, huggingface

# Google Gemini Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-2.0-flash
GOOGLE_EMBEDDING_MODEL=models/embedding-001

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_ORG_ID=your_org_id  # Optional

# Anthropic Claude Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_DEPLOYMENT_NAME=your-deployment-name

# Hugging Face Configuration
HUGGINGFACE_API_KEY=your_huggingface_token
HUGGINGFACE_MODEL=microsoft/DialoGPT-large

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

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# =============================================================================
# EXTERNAL SERVICES (Optional)
# =============================================================================

# Pinecone (if using as vector store)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=rag-documents

# Weaviate (if using as vector store)
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key

# Elasticsearch (for advanced search)
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_password
```

### 🧠 Multiple LLM Provider Support

The application supports multiple LLM providers with automatic fallback:

#### Supported Providers

| Provider | Models | Embedding Models | Features |
|----------|--------|------------------|----------|
| **Google Gemini** | gemini-2.0-flash, gemini-pro | models/embedding-001 | Fast, cost-effective |
| **OpenAI** | gpt-4, gpt-3.5-turbo | text-embedding-3-small/large | High quality, reliable |
| **Anthropic** | claude-3-sonnet, claude-3-haiku | N/A (uses OpenAI embeddings) | Excellent reasoning |
| **Azure OpenAI** | gpt-4, gpt-35-turbo | text-embedding-ada-002 | Enterprise features |
| **Hugging Face** | Various open models | sentence-transformers | Open source, customizable |

#### Provider Configuration Examples

**Google Gemini (Default)**
```env
LLM_PROVIDER=google
GOOGLE_API_KEY=your_api_key
GOOGLE_MODEL=gemini-2.0-flash
```

**OpenAI GPT-4**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**Anthropic Claude**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
# Note: Uses OpenAI for embeddings
OPENAI_API_KEY=your_openai_key_for_embeddings
```

**Azure OpenAI**
```env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=your-gpt4-deployment
```

#### Provider Fallback Chain

Configure multiple providers for automatic fallback:

```env
# Primary provider
LLM_PROVIDER=openai

# Fallback chain (comma-separated)
LLM_FALLBACK_PROVIDERS=google,anthropic

# Configure all provider keys
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
```

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

### Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main/develop branches
- Nightly builds for performance regression

```yaml
# GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Performance Considerations

- **Chunking Strategy**: Optimized chunk size (2000 chars) with overlap (200 chars)
- **Vector Search**: FAISS provides efficient similarity search
- **Caching**: Session-based caching of uploaded documents
- **Async Processing**: FastAPI async endpoints for better concurrency

## Security

- Session-based isolation between users
- File type validation
- File size limits
- SQL injection protection via SQLAlchemy ORM
- Environment variable configuration for sensitive data

## Troubleshooting

### Common Issues

1. **Google API Key Error**
   ```
   Error: Invalid API key
   Solution: Verify GOOGLE_API_KEY in .env file
   ```

2. **File Upload Fails**
   ```
   Error: File too large
   Solution: Check file size limits (10MB max)
   ```

3. **Vector Store Not Found**
   ```
   Error: Vector store not initialized
   Solution: Upload documents first to create the index
   ```

### Logs

Application logs are available in the console. For production deployment, configure proper logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the API documentation at `/docs` endpoint
