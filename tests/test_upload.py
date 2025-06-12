import io

def test_upload_and_metadata(client):
    # 1) Upload a small text file
    file_content = io.BytesIO(b"Hello RAG test")
    response = client.post(
        "/api/upload",
        files={"files": ("test.txt", file_content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    # uploaded_files should include our filename
    assert "uploaded_files" in data
    assert "test.txt" in data["uploaded_files"]

    # 2) Metadata endpoint should list exactly one document
    meta = client.get("/api/metadata").json()
    assert isinstance(meta, list)
    assert len(meta) == 1
    doc = meta[0]
    assert doc["filename"] == "test.txt"
    # num_chunks was computed in upload; ensure it’s > 0
    assert doc["num_chunks"] > 0
