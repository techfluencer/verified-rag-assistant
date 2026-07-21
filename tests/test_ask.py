from app.main import app
from app.rag.router import get_rag_service

class FakeRagService:
    """Stand-in for RagService — no Azure, returns canned data."""

    def ask(self, question: str) -> dict:
        return {"answer": "canned answer", "sources": ["https://example.com/doc"]}
    

def test_ask_returns_answer_and_sources(client):
    # 1. plug the fake into the socket
    app.dependency_overrides[get_rag_service] = lambda: FakeRagService()
    try:
        # 2. call the real endpoint - client.post(...) is not calling your ask() function directly. It's sending a real HTTP request to your app. FastAPI then decides which function to run and builds that function's arguments for you from the request. Those are two different worlds.
        # json= isn't a mock — it's the real request body. json= is a TestClient/httpx feature that serializes your dict to a JSON body and sets Content-Type: application/json. FastAPI reads that body and parses it into AskRequest. It matches the AskRequest shape because that's what the endpoint expects in the body.
        # service is absent because it's injected by FastAPI, not sent by the client.
        response = client.post("/rag/ask", json={"question": "anything"})
        # 3. assert the contract
        assert response.status_code == 200
        assert response.json() == {"answer": "canned answer", "sources": ["https://example.com/doc"]}
    finally:
        # 4. unplug the fake so other tests are unaffected
        app.dependency_overrides.clear()

################ Concept ###################
"""
The problem. Your /rag/ask route needs a RagService. But the real RagService:

--> loads Chroma + creates Azure clients on construction,
--> calls Azure on every ask() → needs creds + network, costs money, is slow, and gives a different answer each time.

If a test hit the real thing, it'd be slow, flaky, and non-deterministic. But what we actually want to test is the endpoint itself — does it accept the request, validate it, call a service, and return the right JSON shape + status? That has nothing to do with Azure. So we want to swap the real brain for a fake one during the test.

The fix — a dependency override. Recall the route gets its service via service = Depends(get_rag_service). It never builds the service itself — it asks for one. That "asking" is a seam we can hijack. FastAPI keeps a dict:

        app.dependency_overrides

You put an entry in it: "when anyone asks for get_rag_service, call THIS instead." Point it at a fake service whose ask() just returns a canned {"answer": ..., "sources": [...]}. No Azure, instant, identical every run.

How the swap works, mechanically:

1. A request hits /rag/ask. FastAPI sees Depends(get_rag_service).
2. Before calling the real get_rag_service, it checks app.dependency_overrides for that key.
3. Finds your override → calls it → the route receives the fake service.
4. The test asserts on the response. Afterward you clear the override so it doesn't leak into other tests.

Why this is the whole point of DI: if we'd written RagService() inside the route, there'd be no seam — you couldn't swap it. Because we injected it via Depends, testing (and swapping implementations in general) becomes trivial.

Analogy: Depends is a socket. In production you plug in the real service; in tests you plug in a fake. dependency_overrides is the switch that decides what's plugged in.
"""

################ Piece by piece explanation of the code ###################
"""
Piece by piece:

1. FakeRagService — note it does not inherit from RagService. Python is duck-typed: the route only ever calls service.ask(...), so anything with an ask() method works. (The service: RagService hint on the route is just for editors — FastAPI doesn't enforce it at runtime.) Its ask() returns a fixed dict → deterministic.
2. app.dependency_overrides[get_rag_service] = lambda: FakeRagService() — the swap. Key = the exact dependency callable the route uses (so we import get_rag_service from the router). Value = a zero-arg callable that returns the fake (a lambda, because FastAPI calls the override like a dependency).
3. client.post("/rag/ask", json={...}) — the client fixture (from conftest.py) sends a real HTTP-style request in-process. The JSON body must satisfy AskRequest.
4. The asserts — because the fake is deterministic, we can check the exact output. This proves the endpoint contract: request parsing (AskRequest) → routing → response shaping (AskResponse) → JSON — all without Azure.
5. finally: app.dependency_overrides.clear() — overrides live on the app object (global), so if we didn't clear it, the fake would leak into test_health and any later test. finally guarantees cleanup even if an assert fails.
"""