import io

def test_query_returns_dummy_answer(client):
    # Upload first so index exists
    file_content = io.BytesIO(b"Some content for testing.")
    client.post(
        "/api/upload",
        files={"files": ("doc1.txt", file_content, "text/plain")}
    )

    # Then query
    response = client.post(
        "/api/query",
        json={"question": "What content?"}
    )
    assert response.status_code == 200
    data = response.json()
    # Because we stubbed ChatGoogleGenerativeAI, answer must be "dummy answer"
    assert data["answer"] == "dummy answer"
