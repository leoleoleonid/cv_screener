import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

from app.services.cvs_preprocessing_service import CVSPreprocessingService


class RAGServiceError(Exception):
    """Base error for RAG service."""


class RAGConfigurationError(RAGServiceError):
    """Raised when mandatory configuration (API key) is missing."""


class RAGIndexNotFoundError(RAGServiceError):
    """Raised when RAG index is missing on disk."""


class RAGEmptyCorpusError(RAGServiceError):
    """Raised when no usable CV text is available for ingestion."""


class RAGService:
    """Handles CV ingestion into FAISS and answers chat queries via RAG."""

    def __init__(
        self,
        cv_service: CVSPreprocessingService,
        index_dir: Path,
        embedding_model: str,
        chat_model: str,
        google_api_key: Optional[str],
    ) -> None:
        self._cv_service = cv_service
        self._index_dir = index_dir
        self._embedding_model = embedding_model
        self._chat_model = chat_model
        self._api_key = google_api_key or ""
        self._rag_chain = None

        if self._api_key and not os.getenv("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = self._api_key

    def ingest(self) -> int:
        """Rebuild FAISS index from CV PDFs, returning number of CVs ingested."""
        self._ensure_api_key()
        cv_texts = self._cv_service.extract_texts()

        documents = self._build_documents(cv_texts)
        if not documents:
            raise RAGEmptyCorpusError("No CV texts found to ingest.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " "],
        )
        chunks = splitter.split_documents(documents)
        if not chunks:
            raise RAGEmptyCorpusError("Unable to create chunks from CV texts.")

        self._clear_index_dir()

        embeddings = GoogleGenerativeAIEmbeddings(
            model=self._embedding_model,
            task_type="RETRIEVAL_DOCUMENT",
        )
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(str(self._index_dir))
        self._rag_chain = None
        return len(documents)

    def answer(self, question: str) -> str:
        """Return an answer using the RAG chain."""
        question = question.strip()
        if not question:
            raise ValueError("Question must not be empty.")

        chain = self._get_chain()
        return chain.invoke(question).strip()

    def _get_chain(self):
        if self._rag_chain is None:
            self._rag_chain = self._build_chain()
        return self._rag_chain

    def _build_chain(self):
        retriever = self._load_retriever()
        prompt = ChatPromptTemplate.from_template(
            """
You are an AI assistant helping with CV screening and candidate analysis.

Use ONLY the information provided inside <context>. If the CVs do not mention
something, explicitly state that it is not present in the available CVs.

<context>
{context}
</context>

User question:
{question}
""".strip()
        )
        llm = ChatGoogleGenerativeAI(
            model=self._chat_model,
            temperature=0.1,
        )
        chain = (
            {
                "question": RunnablePassthrough(),
                "context": retriever | self._format_docs,
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain

    def _load_retriever(self):
        self._ensure_api_key()
        if not self._index_dir.exists():
            raise RAGIndexNotFoundError("RAG index is not built yet.")

        embeddings = GoogleGenerativeAIEmbeddings(
            model=self._embedding_model,
            task_type="RETRIEVAL_QUERY",
        )
        vectorstore = FAISS.load_local(
            str(self._index_dir),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        return vectorstore.as_retriever(search_kwargs={"k": 4})

    def _build_documents(self, cv_texts: Dict[str, str]) -> List[Document]:
        documents: List[Document] = []
        for filename, text in cv_texts.items():
            normalized = text.strip()
            if not normalized:
                continue
            documents.append(
                Document(page_content=normalized, metadata={"filename": filename})
            )
        return documents

    def _format_docs(self, docs: List[Document]) -> str:
        if not docs:
            return "No CV context retrieved."
        formatted = []
        for doc in docs:
            filename = doc.metadata.get("filename", "unknown")
            formatted.append(f"File: {filename}\n{doc.page_content}")
        return "\n\n".join(formatted)

    def _clear_index_dir(self) -> None:
        self._index_dir.mkdir(parents=True, exist_ok=True)
        for child in self._index_dir.iterdir():
            if child.is_file() or child.is_symlink():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)

    def _ensure_api_key(self) -> None:
        if not self._api_key:
            raise RAGConfigurationError("Google API key is required for RAG features.")
