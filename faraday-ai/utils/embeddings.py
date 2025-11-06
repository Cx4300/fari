"""
FARADAY AI - Embeddings Utilities
Helper functions for text embeddings
"""

from typing import List, Union
from langchain_community.embeddings import HuggingFaceEmbeddings

from config.settings import settings
from utils.logger import logger


_embeddings_instance = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Get or create embeddings model singleton.

    Returns:
        HuggingFaceEmbeddings instance
    """
    global _embeddings_instance

    if _embeddings_instance is None:
        try:
            logger.info(f"🔧 Loading embeddings model: {settings.rag.embedding_model}")

            _embeddings_instance = HuggingFaceEmbeddings(
                model_name=settings.rag.embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

            logger.info("✅ Embeddings model loaded")

        except Exception as e:
            logger.error(f"❌ Failed to load embeddings model: {e}")
            raise

    return _embeddings_instance


async def embed_text(text: str) -> List[float]:
    """
    Generate embedding for single text.

    Args:
        text: Input text

    Returns:
        Embedding vector
    """
    try:
        embeddings = get_embeddings()
        embedding = embeddings.embed_query(text)
        return embedding
    except Exception as e:
        logger.error(f"❌ Error generating embedding: {e}")
        raise


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.

    Args:
        texts: List of input texts

    Returns:
        List of embedding vectors
    """
    try:
        embeddings = get_embeddings()
        embedding_vectors = embeddings.embed_documents(texts)
        return embedding_vectors
    except Exception as e:
        logger.error(f"❌ Error generating embeddings: {e}")
        raise


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score (0-1)
    """
    import numpy as np

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(dot_product / (norm1 * norm2))


# Export
__all__ = ['get_embeddings', 'embed_text', 'embed_texts', 'cosine_similarity']
