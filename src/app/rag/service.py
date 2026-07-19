from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from app.config import settings

# Grounded prompt — the faithfulness lever (cite only when answering; else "I don't know")
PROMPT = ChatPromptTemplate.from_template(
    "Answer the question using ONLY the context below.\n"
    "If the answer is not in the context, reply exactly: I don't know.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}"
)

class RagService:
    """Loads the persisted vector store once, then answers questions against it."""

    def __init__(self) -> None:
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_deployment=settings.azure_openai_embedding_deployment,
        )
        store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=embeddings,
            persist_directory=settings.persist_dir, # READ the index built earlier
        )
        self._retriever =  store.as_retriever(search_kwargs={"k": settings.retrieve_k})
        self._llm =  AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_deployment=settings.azure_openai_chat_deployment,
            temperature=0,
        )

    @staticmethod
    def _format_context(docs) -> str:
        return "\n\n".join(f"[Source: {d.metadata.get('source')}]\n{d.page_content}" for d in docs)
    
    def ask(self, question: str) -> dict:
        docs =  self._retriever.invoke(question)
        answer = self._llm.invoke(
            PROMPT.format(context=self._format_context(docs), question=question)
            ).content
        
        # No grounded answer → no sources
        if answer.strip().lower().startswith("i don't know"):
            return {"answer": answer, "sources": []}

        sources = list(dict.fromkeys(d.metadata.get('source') for d in docs)) 
        # unique, ordered
        return {"answer": answer, "sources": sources}


        

