from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.rag.router import router as rag_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Verified RAG Assistant",
        description="RAG over docs with grounded, cited answers.",
        version="0.1.0"
    )

    # Let the React (Vite) dev server call the API from the browser
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    def health() -> dict:
        return {"status": "ok"}
    
    app.include_router(rag_router)
    return app

app = create_app()