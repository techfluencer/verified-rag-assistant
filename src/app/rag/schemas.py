from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Incoming question from the client."""

    question: str = Field(
        min_length=1, # Automatic request validation — min_length=1 means an empty question is rejected with a clean 422 error before your code runs. No manual 'if not question' checks.
        description="The user's question about the document corpus.",
        examples=["Which text splitter is recommended?"],
    )


class AskResponse(BaseModel):
    """Grounded answer plus the source pages it was drawn from."""

    answer: str = Field(
        examples=["The recommended text splitter is the RecursiveCharacterTextSplitter."]
    )
    sources: list[str] = Field(
        default_factory=list,
        description="URLs of the pages retrieved to ground the answer (empty if unknown).",
    )