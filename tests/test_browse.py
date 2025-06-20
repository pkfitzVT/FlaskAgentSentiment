def test_browse_status(client):
    resp = client.get("/browse")
    assert resp.status_code == 200
    assert b"<table" in resp.data
