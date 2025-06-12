import io
import time
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed


def test_upload_performance(client):
    """Test upload performance with multiple files"""
    
    start_time = time.time()
    
    # Create multiple test files
    files = []
    for i in range(10):
        content = f"Performance test document {i}. " * 100  # ~2.5KB each
        file_obj = io.BytesIO(content.encode())
        files.append(("files", (f"perf_test_{i}.txt", file_obj, "text/plain")))
    
    # Upload all files
    response = client.post("/api/upload", files=files)
    
    end_time = time.time()
    upload_time = end_time - start_time
    
    assert response.status_code == 200
    assert len(response.json()["uploaded_files"]) == 10
    
    # Upload should complete within reasonable time (adjust threshold as needed)
    assert upload_time < 30.0, f"Upload took {upload_time:.2f} seconds, which is too long"
    
    print(f"Upload performance: {upload_time:.2f} seconds for 10 files")


def test_query_performance(client):
    """Test query response time"""
    
    # First upload a document
    content = "Performance testing document with various topics including AI, ML, data science, and technology."
    doc = io.BytesIO(content.encode())
    
    upload_response = client.post(
        "/api/upload",
        files={"files": ("perf_doc.txt", doc, "text/plain")}
    )
    assert upload_response.status_code == 200
    
    # Test query performance
    queries = [
        "What is this document about?",
        "Tell me about AI and ML",
        "What topics are covered?",
        "Explain the main concepts",
        "What is data science?"
    ]
    
    query_times = []
    
    for query in queries:
        start_time = time.time()
        
        response = client.post(
            "/api/query",
            json={"question": query}
        )
        
        end_time = time.time()
        query_time = end_time - start_time
        query_times.append(query_time)
        
        assert response.status_code == 200
        assert "answer" in response.json()
    
    avg_query_time = sum(query_times) / len(query_times)
    max_query_time = max(query_times)
    
    # Queries should be reasonably fast (adjust thresholds as needed)
    assert avg_query_time < 5.0, f"Average query time {avg_query_time:.2f}s is too slow"
    assert max_query_time < 10.0, f"Max query time {max_query_time:.2f}s is too slow"
    
    print(f"Query performance: avg={avg_query_time:.2f}s, max={max_query_time:.2f}s")


def test_concurrent_queries(client):
    """Test handling concurrent queries"""
    
    # Upload a document first
    content = "Concurrent testing document with information about various subjects."
    doc = io.BytesIO(content.encode())
    
    upload_response = client.post(
        "/api/upload",
        files={"files": ("concurrent_doc.txt", doc, "text/plain")}
    )
    assert upload_response.status_code == 200
    
    def make_query(query_text):
        """Helper function to make a query"""
        start_time = time.time()
        response = client.post(
            "/api/query",
            json={"question": query_text}
        )
        end_time = time.time()
        return {
            "status_code": response.status_code,
            "response_time": end_time - start_time,
            "query": query_text
        }
    
    # Create multiple concurrent queries
    queries = [
        f"What is query {i} about?" for i in range(5)
    ]
    
    start_time = time.time()
    
    # Execute queries concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_query = {
            executor.submit(make_query, query): query 
            for query in queries
        }
        
        results = []
        for future in as_completed(future_to_query):
            result = future.result()
            results.append(result)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # All queries should succeed
    assert len(results) == 5
    for result in results:
        assert result["status_code"] == 200
    
    # Concurrent execution should be faster than sequential
    avg_response_time = sum(r["response_time"] for r in results) / len(results)
    
    print(f"Concurrent query performance: total={total_time:.2f}s, avg_individual={avg_response_time:.2f}s")
    
    # Total time should be less than sum of individual times (due to concurrency)
    assert total_time < sum(r["response_time"] for r in results)


def test_memory_usage_with_large_documents(client):
    """Test memory usage with larger documents"""
    
    # Create a larger document (but within limits)
    large_content = "This is a large document for memory testing. " * 10000  # ~450KB
    large_doc = io.BytesIO(large_content.encode())
    
    start_time = time.time()
    
    upload_response = client.post(
        "/api/upload",
        files={"files": ("large_doc.txt", large_doc, "text/plain")}
    )
    
    upload_time = time.time() - start_time
    
    assert upload_response.status_code == 200
    
    # Check that document was properly chunked
    metadata = client.get("/api/metadata").json()
    assert len(metadata) == 1
    doc = metadata[0]
    assert doc["num_chunks"] > 10  # Should be split into many chunks
    
    # Test querying the large document
    query_start = time.time()
    query_response = client.post(
        "/api/query",
        json={"question": "What is this large document about?"}
    )
    query_time = time.time() - query_start
    
    assert query_response.status_code == 200
    
    print(f"Large document performance: upload={upload_time:.2f}s, query={query_time:.2f}s, chunks={doc['num_chunks']}")


def test_metadata_retrieval_performance(client):
    """Test metadata retrieval performance with many documents"""
    
    # Upload multiple documents
    files = []
    for i in range(15):  # Upload 15 documents
        content = f"Metadata test document {i} with unique content."
        file_obj = io.BytesIO(content.encode())
        files.append(("files", (f"meta_test_{i}.txt", file_obj, "text/plain")))
    
    # Upload in batches to avoid overwhelming the system
    batch_size = 5
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        response = client.post("/api/upload", files=batch)
        assert response.status_code == 200
    
    # Test metadata retrieval performance
    start_time = time.time()
    
    metadata_response = client.get("/api/metadata")
    
    end_time = time.time()
    retrieval_time = end_time - start_time
    
    assert metadata_response.status_code == 200
    metadata = metadata_response.json()
    assert len(metadata) == 15
    
    # Metadata retrieval should be fast
    assert retrieval_time < 2.0, f"Metadata retrieval took {retrieval_time:.2f}s, which is too slow"
    
    print(f"Metadata retrieval performance: {retrieval_time:.2f}s for {len(metadata)} documents")


def test_stress_test_file_limits(client):
    """Test system behavior at file limits"""
    
    # Test uploading exactly the maximum number of files (20)
    files = []
    for i in range(20):
        content = f"Stress test document {i}."
        file_obj = io.BytesIO(content.encode())
        files.append(("files", (f"stress_{i}.txt", file_obj, "text/plain")))
    
    start_time = time.time()
    
    # Upload all 20 files at once
    response = client.post("/api/upload", files=files)
    
    upload_time = time.time() - start_time
    
    assert response.status_code == 200
    upload_data = response.json()
    assert len(upload_data["uploaded_files"]) == 20
    
    # Verify all documents are in metadata
    metadata = client.get("/api/metadata").json()
    assert len(metadata) == 20
    
    # Test that 21st file is rejected
    extra_file = io.BytesIO(b"This should be rejected")
    extra_response = client.post(
        "/api/upload",
        files={"files": ("extra.txt", extra_file, "text/plain")}
    )
    
    # Should return 400 due to file limit
    assert extra_response.status_code == 400
    
    print(f"Stress test performance: {upload_time:.2f}s for 20 files")


@pytest.mark.slow
def test_endurance_queries(client):
    """Test system stability with many consecutive queries"""
    
    # Upload a document
    content = "Endurance test document with comprehensive content for testing."
    doc = io.BytesIO(content.encode())
    
    upload_response = client.post(
        "/api/upload",
        files={"files": ("endurance_doc.txt", doc, "text/plain")}
    )
    assert upload_response.status_code == 200
    
    # Perform many consecutive queries
    num_queries = 50
    query_times = []
    
    for i in range(num_queries):
        start_time = time.time()
        
        response = client.post(
            "/api/query",
            json={"question": f"Query number {i}: What is this about?"}
        )
        
        end_time = time.time()
        query_time = end_time - start_time
        query_times.append(query_time)
        
        assert response.status_code == 200
        
        # Optional: Add small delay to simulate real usage
        time.sleep(0.1)
    
    avg_time = sum(query_times) / len(query_times)
    min_time = min(query_times)
    max_time = max(query_times)
    
    # Check for performance degradation
    first_half_avg = sum(query_times[:25]) / 25
    second_half_avg = sum(query_times[25:]) / 25
    
    # Performance shouldn't degrade significantly over time
    degradation_ratio = second_half_avg / first_half_avg
    assert degradation_ratio < 2.0, f"Performance degraded by {degradation_ratio:.2f}x"
    
    print(f"Endurance test: {num_queries} queries, avg={avg_time:.2f}s, min={min_time:.2f}s, max={max_time:.2f}s")
    print(f"Performance stability: first_half={first_half_avg:.2f}s, second_half={second_half_avg:.2f}s")
