def test_analyze_status(client):
    resp = client.get("/analyze")
    assert resp.status_code == 200
    assert b"Analysis Dashboard" in resp.data
