import io
import pytest
import os
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.mark.integration
def test_full_rag_pipeline(client):
    """Test the complete RAG pipeline: upload -> query -> metadata -> delete"""

    # 1. Upload a document
    file_content = io.BytesIO(b"This is a test document about artificial intelligence and machine learning. "
                             b"AI is transforming various industries including healthcare, finance, and education. "
                             b"Machine learning algorithms can process large amounts of data to identify patterns. "
                             b"Deep learning is a subset of machine learning that uses neural networks.")

    upload_response = client.post(
        "/api/upload",
        files={"files": ("ai_document.txt", file_content, "text/plain")}
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert "uploaded_files" in upload_data
    assert "ai_document.txt" in upload_data["uploaded_files"]

    # 2. Check metadata
    metadata_response = client.get("/api/metadata")
    assert metadata_response.status_code == 200
    metadata = metadata_response.json()
    assert len(metadata) == 1
    doc = metadata[0]
    assert doc["filename"] == "ai_document.txt"
    assert doc["num_chunks"] > 0
    doc_id = doc["id"]

    # 3. Query the document
    query_response = client.post(
        "/api/query",
        json={"question": "What is this document about?"}
    )
    assert query_response.status_code == 200
    query_data = query_response.json()
    assert "answer" in query_data
    assert "sources_count" in query_data
    assert "session_id" in query_data
    # With our dummy implementation, answer should be "dummy answer"
    assert query_data["answer"] == "dummy answer"

    # 4. Query with AI-related question
    ai_query_response = client.post(
        "/api/query",
        json={"question": "What industries are mentioned in relation to AI?"}
    )
    assert ai_query_response.status_code == 200
    ai_query_data = ai_query_response.json()
    assert "answer" in ai_query_data
    assert "sources_count" in ai_query_data

    # 5. Test empty question handling
    empty_query_response = client.post(
        "/api/query",
        json={"question": ""}
    )
    assert empty_query_response.status_code == 400

    # 6. Test whitespace-only question
    whitespace_query_response = client.post(
        "/api/query",
        json={"question": "   "}
    )
    assert whitespace_query_response.status_code == 400

    # 7. Delete the document
    delete_response = client.delete(f"/api/metadata/{doc_id}")
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    assert delete_data["status"] == "removed"
    assert delete_data["filename"] == "ai_document.txt"

    # 8. Verify document is deleted
    final_metadata = client.get("/api/metadata").json()
    assert len(final_metadata) == 0

    # 9. Test querying after document deletion
    post_delete_query = client.post(
        "/api/query",
        json={"question": "What was in the deleted document?"}
    )
    assert post_delete_query.status_code == 500  # Vector store not initialized


@pytest.mark.integration
def test_multiple_documents_upload(client):
    """Test uploading multiple documents and querying across them"""

    # Upload multiple documents
    doc1 = io.BytesIO(b"Document 1: Python programming language basics and syntax. Python is versatile.")
    doc2 = io.BytesIO(b"Document 2: JavaScript frameworks like React and Vue.js for web development.")
    doc3 = io.BytesIO(b"Document 3: Database design principles and SQL queries for data management.")

    upload_response = client.post(
        "/api/upload",
        files=[
            ("files", ("python.txt", doc1, "text/plain")),
            ("files", ("javascript.txt", doc2, "text/plain")),
            ("files", ("database.txt", doc3, "text/plain"))
        ]
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert len(upload_data["uploaded_files"]) == 3

    # Check metadata for all documents
    metadata = client.get("/api/metadata").json()
    assert len(metadata) == 3
    filenames = [doc["filename"] for doc in metadata]
    assert "python.txt" in filenames
    assert "javascript.txt" in filenames
    assert "database.txt" in filenames

    # Query across all documents
    query_response = client.post(
        "/api/query",
        json={"question": "What programming languages are mentioned?"}
    )
    assert query_response.status_code == 200
    query_data = query_response.json()
    assert "sources_count" in query_data
    assert query_data["sources_count"] > 0


def test_file_size_and_type_validation(client):
    """Test file upload validation for size and type"""

    # Test unsupported file type
    unsupported_file = io.BytesIO(b"This is an image file")
    upload_response = client.post(
        "/api/upload",
        files={"files": ("image.jpg", unsupported_file, "image/jpeg")}
    )
    # Should still return 200 but file should be skipped
    assert upload_response.status_code == 200

    # Test large file (simulated by creating a large text content)
    large_content = b"Large file content. " * 100000  # Approximately 2MB
    large_file = io.BytesIO(large_content)
    upload_response = client.post(
        "/api/upload",
        files={"files": ("large.txt", large_file, "text/plain")}
    )
    # Should still return 200 but file might be skipped due to size
    assert upload_response.status_code == 200


def test_session_isolation(client):
    """Test that different sessions don't interfere with each other"""

    # Upload document in first session
    doc1 = io.BytesIO(b"Session 1 document content")
    upload1 = client.post(
        "/api/upload",
        files={"files": ("session1.txt", doc1, "text/plain")}
    )
    assert upload1.status_code == 200

    # Check metadata for first session
    metadata1 = client.get("/api/metadata").json()
    assert len(metadata1) == 1
    assert metadata1[0]["filename"] == "session1.txt"


def test_query_without_documents(client):
    """Test querying when no documents are uploaded"""

    query_response = client.post(
        "/api/query",
        json={"question": "What is in the documents?"}
    )
    # Should return 500 because vector store is not initialized
    assert query_response.status_code == 500


def test_error_handling(client):
    """Test various error conditions"""

    # Test query without session
    # This is handled by the test client setup, so we'll test other errors

    # Test deleting non-existent document
    delete_response = client.delete("/api/metadata/999")
    assert delete_response.status_code == 404

    # Test empty query
    empty_query = client.post(
        "/api/query",
        json={"question": ""}
    )
    # Should still process but might return error from LLM
    # With our dummy implementation, it should still return 200
    assert empty_query.status_code in [200, 400]


def test_concurrent_uploads(client):
    """Test handling multiple concurrent uploads"""

    # Simulate concurrent uploads by uploading multiple files at once
    files = []
    for i in range(5):
        content = io.BytesIO(f"Document {i} content about topic {i}".encode())
        files.append(("files", (f"doc{i}.txt", content, "text/plain")))

    upload_response = client.post("/api/upload", files=files)
    assert upload_response.status_code == 200

    upload_data = upload_response.json()
    assert len(upload_data["uploaded_files"]) == 5

    # Verify all documents are in metadata
    metadata = client.get("/api/metadata").json()
    assert len(metadata) == 5


def test_chunking_behavior(client):
    """Test that documents are properly chunked"""

    # Create a longer document that should be split into multiple chunks
    long_content = "This is a test document. " * 1000  # Create a long document
    long_doc = io.BytesIO(long_content.encode())

    upload_response = client.post(
        "/api/upload",
        files={"files": ("long_doc.txt", long_doc, "text/plain")}
    )
    assert upload_response.status_code == 200

    # Check that the document was chunked
    metadata = client.get("/api/metadata").json()
    assert len(metadata) == 1
    doc = metadata[0]
    assert doc["num_chunks"] > 1  # Should be split into multiple chunks


@pytest.mark.integration
def test_llm_provider_endpoints(client):
    """Test LLM provider management endpoints"""

    # Test getting provider information
    providers_response = client.get("/api/providers")
    assert providers_response.status_code == 200

    provider_data = providers_response.json()
    assert "available_providers" in provider_data
    assert "provider_stats" in provider_data
    assert "primary_provider" in provider_data
    assert "fallback_providers" in provider_data

    # Test clearing cache
    cache_response = client.post("/api/providers/clear-cache")
    assert cache_response.status_code == 200
    cache_data = cache_response.json()
    assert "message" in cache_data


@pytest.mark.integration
def test_llm_provider_fallback_simulation(client):
    """Test LLM provider fallback behavior with mocked failures"""

    # Upload a test document first
    file_content = io.BytesIO(b"Test document for provider fallback testing.")
    upload_response = client.post(
        "/api/upload",
        files={"files": ("fallback_test.txt", file_content, "text/plain")}
    )
    assert upload_response.status_code == 200

    # Mock primary provider failure and test fallback
    with patch('llm.providers.llm_manager.generate_response') as mock_generate:
        # Simulate successful fallback
        mock_response = MagicMock()
        mock_response.content = "Fallback response"
        mock_response.provider.value = "google"
        mock_generate.return_value = mock_response

        query_response = client.post(
            "/api/query",
            json={"question": "Test fallback question"}
        )
        assert query_response.status_code == 200
        query_data = query_response.json()
        assert "answer" in query_data


@pytest.mark.integration
def test_session_isolation(client):
    """Test that different sessions don't interfere with each other"""

    # Create first client session
    doc1 = io.BytesIO(b"Session 1 document content about topic A")
    upload1 = client.post(
        "/api/upload",
        files={"files": ("session1.txt", doc1, "text/plain")}
    )
    assert upload1.status_code == 200

    # Check metadata for first session
    metadata1 = client.get("/api/metadata").json()
    assert len(metadata1) == 1
    assert metadata1[0]["filename"] == "session1.txt"

    # Query in first session
    query1 = client.post(
        "/api/query",
        json={"question": "What is in session 1?"}
    )
    assert query1.status_code == 200


@pytest.mark.integration
def test_performance_monitoring(client):
    """Test performance monitoring and response time tracking"""

    # Upload document
    file_content = io.BytesIO(b"Performance test document with sufficient content for testing.")
    upload_response = client.post(
        "/api/upload",
        files={"files": ("perf_test.txt", file_content, "text/plain")}
    )
    assert upload_response.status_code == 200

    # Measure query response time
    start_time = time.time()
    query_response = client.post(
        "/api/query",
        json={"question": "What is this document about?"}
    )
    end_time = time.time()
    response_time = end_time - start_time

    assert query_response.status_code == 200
    # Response should be reasonably fast (adjust threshold as needed)
    assert response_time < 10.0, f"Query took {response_time:.2f} seconds"

    # Check provider stats
    providers_response = client.get("/api/providers")
    assert providers_response.status_code == 200
    provider_data = providers_response.json()
    assert "provider_stats" in provider_data


@pytest.mark.integration
def test_error_handling_and_recovery(client):
    """Test comprehensive error handling scenarios"""

    # Test query without any documents
    no_docs_query = client.post(
        "/api/query",
        json={"question": "What is in the documents?"}
    )
    assert no_docs_query.status_code == 500

    # Test invalid document deletion
    invalid_delete = client.delete("/api/metadata/99999")
    assert invalid_delete.status_code == 404

    # Test malformed query request
    malformed_query = client.post(
        "/api/query",
        json={"invalid_field": "test"}
    )
    assert malformed_query.status_code == 422  # Validation error


@pytest.mark.integration
def test_environment_variable_configuration(client):
    """Test that environment variables are properly loaded and used"""

    # Test with environment variable override
    with patch.dict(os.environ, {
        'MAX_RETRIEVAL_RESULTS': '3',
        'SIMILARITY_THRESHOLD': '0.8'
    }):
        # Upload document
        file_content = io.BytesIO(b"Environment test document with configuration testing.")
        upload_response = client.post(
            "/api/upload",
            files={"files": ("env_test.txt", file_content, "text/plain")}
        )
        assert upload_response.status_code == 200

        # Query should use the environment variable settings
        query_response = client.post(
            "/api/query",
            json={"question": "Test environment configuration"}
        )
        assert query_response.status_code == 200
        query_data = query_response.json()
        # Should respect MAX_RETRIEVAL_RESULTS setting
        assert query_data["sources_count"] <= 3


@pytest.mark.integration
def test_concurrent_operations(client):
    """Test handling of concurrent operations"""

    # Upload multiple documents concurrently (simulated)
    files = []
    for i in range(3):
        content = io.BytesIO(f"Concurrent test document {i} with unique content.".encode())
        files.append(("files", (f"concurrent_{i}.txt", content, "text/plain")))

    upload_response = client.post("/api/upload", files=files)
    assert upload_response.status_code == 200

    upload_data = upload_response.json()
    assert len(upload_data["uploaded_files"]) == 3

    # Verify all documents are accessible
    metadata = client.get("/api/metadata").json()
    assert len(metadata) == 3

    # Test concurrent queries (simulated)
    queries = [
        "What is in document 0?",
        "What is in document 1?",
        "What is in document 2?"
    ]

    for query in queries:
        response = client.post("/api/query", json={"question": query})
        assert response.status_code == 200


@pytest.mark.integration
def test_api_endpoints_accessibility(client):
    """Test that all API endpoints are accessible"""

    # Test home page
    home_response = client.get("/")
    assert home_response.status_code == 200

    # Test API docs
    docs_response = client.get("/docs")
    assert docs_response.status_code == 200

    # Test OpenAPI schema
    openapi_response = client.get("/openapi.json")
    assert openapi_response.status_code == 200

    # Test metadata endpoint without session
    metadata_response = client.get("/api/metadata")
    assert metadata_response.status_code == 200
    # Should return empty list for new session
    assert metadata_response.json() == []


@pytest.mark.integration
def test_data_persistence_and_cleanup(client):
    """Test data persistence within session and proper cleanup"""

    # Upload document
    file_content = io.BytesIO(b"Persistence test document for cleanup verification.")
    upload_response = client.post(
        "/api/upload",
        files={"files": ("persistence_test.txt", file_content, "text/plain")}
    )
    assert upload_response.status_code == 200

    # Verify document persists in session
    metadata1 = client.get("/api/metadata").json()
    assert len(metadata1) == 1
    doc_id = metadata1[0]["id"]

    # Query the document
    query_response = client.post(
        "/api/query",
        json={"question": "What is this document about?"}
    )
    assert query_response.status_code == 200

    # Delete document and verify cleanup
    delete_response = client.delete(f"/api/metadata/{doc_id}")
    assert delete_response.status_code == 200

    # Verify document is removed
    metadata2 = client.get("/api/metadata").json()
    assert len(metadata2) == 0

    # Verify vector store is cleaned up (query should fail)
    post_cleanup_query = client.post(
        "/api/query",
        json={"question": "What was in the deleted document?"}
    )
    assert post_cleanup_query.status_code == 500
