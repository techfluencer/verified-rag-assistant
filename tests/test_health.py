"""
TestClient(app) calls your app in-process — it exercises real routing, DI, and response models without starting uvicorn or a network. Fast and reliable.

The test names client as a parameter → pytest injects the fixture.
"""

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}