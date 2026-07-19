from functools import lru_cache

from fastapi import APIRouter, Depends

from app.rag.schemas import AskRequest, AskResponse
from app.rag.service import RagService

router = APIRouter(prefix="/rag", tags=["rag"]) #  groups this feature's routes (endpoint becomes POST /rag/ask; tags groups it in Swagger)

# @lru_cache on get_rag_service — this is your singleton. lru_cache means the function runs once, then returns the same RagService forever. So the expensive Chroma+Azure setup happens once, on the first request. Clean, and testable (tests can override it with a fake).
@lru_cache
def get_rag_service() -> RagService:
    """Build RagService once, reuse it — app-scoped singleton (created on first request)."""
    return RagService()

# Depends(get_rag_service) — FastAPI's dependency injection: it calls the provider and hands the service to your route. The route never constructs the service itself → loose coupling.
# response_model=AskResponse — validates + shapes the output and documents it.
@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, service: RagService = Depends(get_rag_service)) -> AskResponse:
    result = service.ask(request.question)
    return AskResponse(**result)




