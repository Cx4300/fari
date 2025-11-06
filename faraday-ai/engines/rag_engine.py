"""
FARADAY AI - RAG Engine
LangChain + FAISS + HuggingFace embeddings for document search
"""

import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from config.settings import settings
from utils.logger import logger
from utils.document_loader import load_pdf, load_docx, load_txt, load_markdown, load_csv


class RAGEngine:
    """
    RAG (Retrieval-Augmented Generation) Engine.
    Handles document loading, chunking, embedding, and semantic search.
    """

    def __init__(self):
        """Initialize RAG Engine"""
        self.config = settings.rag
        self.vectorstore = None
        self.embeddings = None
        self.documents = []

        logger.info("🔧 Initializing RAG Engine...")
        self._initialize_embeddings()

    def _initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.config.embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info(f"✅ Embeddings initialized: {self.config.embedding_model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize embeddings: {e}")
            raise

    async def load_documents_from_directory(self, directory: Optional[Path] = None) -> int:
        """
        Load documents from directory.

        Args:
            directory: Directory path (default: settings.documents_dir)

        Returns:
            Number of documents loaded
        """
        try:
            directory = directory or settings.documents_dir
            logger.info(f"📚 Loading documents from: {directory}")

            if not directory.exists():
                logger.warning(f"⚠️  Directory does not exist: {directory}")
                return 0

            loaded_docs = []

            # Load all supported files
            for file_path in directory.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.config.supported_extensions:
                    try:
                        docs = await self._load_file(file_path)
                        loaded_docs.extend(docs)
                        logger.info(f"✅ Loaded: {file_path.name} ({len(docs)} chunks)")
                    except Exception as e:
                        logger.error(f"❌ Failed to load {file_path.name}: {e}")

            if loaded_docs:
                self.documents.extend(loaded_docs)
                await self._build_vectorstore(loaded_docs)
                logger.info(f"✅ Total documents loaded: {len(loaded_docs)}")
            else:
                logger.warning("⚠️  No documents loaded")

            return len(loaded_docs)

        except Exception as e:
            logger.error(f"❌ Error loading documents: {e}")
            return 0

    async def load_document(self, file_path: Path) -> int:
        """
        Load a single document.

        Args:
            file_path: Path to document

        Returns:
            Number of chunks created
        """
        try:
            docs = await self._load_file(file_path)

            if docs:
                self.documents.extend(docs)
                await self._build_vectorstore(docs)
                logger.info(f"✅ Loaded document: {file_path.name} ({len(docs)} chunks)")
                return len(docs)

            return 0

        except Exception as e:
            logger.error(f"❌ Error loading document {file_path}: {e}")
            return 0

    async def _load_file(self, file_path: Path) -> List[Document]:
        """
        Load file based on extension.

        Args:
            file_path: Path to file

        Returns:
            List of LangChain Documents
        """
        extension = file_path.suffix.lower()

        if extension == ".pdf":
            return await load_pdf(file_path)
        elif extension == ".docx":
            return await load_docx(file_path)
        elif extension == ".txt":
            return await load_txt(file_path)
        elif extension == ".md":
            return await load_markdown(file_path)
        elif extension == ".csv":
            return await load_csv(file_path)
        else:
            logger.warning(f"⚠️  Unsupported file type: {extension}")
            return []

    async def _build_vectorstore(self, documents: List[Document]):
        """
        Build or update FAISS vectorstore.

        Args:
            documents: List of documents to add
        """
        try:
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
                length_function=len,
            )

            chunks = text_splitter.split_documents(documents)
            logger.info(f"📄 Split into {len(chunks)} chunks")

            # Create or update vectorstore
            if self.vectorstore is None:
                # Create new vectorstore
                self.vectorstore = await asyncio.to_thread(
                    FAISS.from_documents,
                    chunks,
                    self.embeddings
                )
                logger.info("✅ Vectorstore created")
            else:
                # Add to existing vectorstore
                await asyncio.to_thread(
                    self.vectorstore.add_documents,
                    chunks
                )
                logger.info("✅ Vectorstore updated")

            # Save vectorstore
            await self._save_vectorstore()

        except Exception as e:
            logger.error(f"❌ Error building vectorstore: {e}")
            raise

    async def _save_vectorstore(self):
        """Save vectorstore to disk"""
        try:
            if self.vectorstore:
                save_path = str(self.config.vector_store_path)
                await asyncio.to_thread(
                    self.vectorstore.save_local,
                    save_path
                )
                logger.info(f"💾 Vectorstore saved to: {save_path}")
        except Exception as e:
            logger.error(f"❌ Error saving vectorstore: {e}")

    async def load_vectorstore(self):
        """Load vectorstore from disk"""
        try:
            save_path = str(self.config.vector_store_path)
            index_path = Path(save_path) / "index.faiss"

            if index_path.exists():
                self.vectorstore = await asyncio.to_thread(
                    FAISS.load_local,
                    save_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"✅ Vectorstore loaded from: {save_path}")
                return True
            else:
                logger.info("ℹ️  No saved vectorstore found")
                return False

        except Exception as e:
            logger.error(f"❌ Error loading vectorstore: {e}")
            return False

    async def search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Perform semantic search.

        Args:
            query: Search query
            k: Number of results (default: config.top_k_results)

        Returns:
            List of relevant documents
        """
        try:
            if self.vectorstore is None:
                logger.warning("⚠️  Vectorstore not initialized")
                return []

            k = k or self.config.top_k_results

            results = await asyncio.to_thread(
                self.vectorstore.similarity_search,
                query,
                k=k
            )

            logger.info(f"🔍 Found {len(results)} results for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"❌ Error searching: {e}")
            return []

    async def search_with_scores(self, query: str, k: Optional[int] = None) -> List[tuple]:
        """
        Perform semantic search with similarity scores.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of (Document, score) tuples
        """
        try:
            if self.vectorstore is None:
                logger.warning("⚠️  Vectorstore not initialized")
                return []

            k = k or self.config.top_k_results

            results = await asyncio.to_thread(
                self.vectorstore.similarity_search_with_score,
                query,
                k=k
            )

            # Filter by similarity threshold
            filtered_results = [
                (doc, score) for doc, score in results
                if score >= self.config.similarity_threshold
            ]

            logger.info(f"🔍 Found {len(filtered_results)} results (threshold: {self.config.similarity_threshold})")
            return filtered_results

        except Exception as e:
            logger.error(f"❌ Error searching with scores: {e}")
            return []

    async def get_context_for_query(self, query: str, k: Optional[int] = None) -> str:
        """
        Get formatted context for LLM prompt.

        Args:
            query: Search query
            k: Number of results

        Returns:
            Formatted context string
        """
        try:
            results = await self.search(query, k)

            if not results:
                return "No relevant documents found."

            context_parts = []
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get('source', 'Unknown')
                content = doc.page_content.strip()
                context_parts.append(f"[Document {i} - {source}]\n{content}\n")

            context = "\n---\n".join(context_parts)
            logger.info(f"📝 Generated context ({len(context)} chars)")

            return context

        except Exception as e:
            logger.error(f"❌ Error getting context: {e}")
            return "Error retrieving context."

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG engine statistics"""
        return {
            "total_documents": len(self.documents),
            "vectorstore_initialized": self.vectorstore is not None,
            "embedding_model": self.config.embedding_model,
            "chunk_size": self.config.chunk_size,
            "chunk_overlap": self.config.chunk_overlap,
        }

    async def clear(self):
        """Clear all documents and vectorstore"""
        self.documents = []
        self.vectorstore = None
        logger.info("🗑️  RAG Engine cleared")


# Singleton instance
_rag_engine_instance = None


def get_rag_engine() -> RAGEngine:
    """Get or create RAG Engine singleton"""
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance


# Export
__all__ = ['RAGEngine', 'get_rag_engine']
