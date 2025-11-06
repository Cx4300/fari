"""
FARADAY AI - Document Loader
Load documents from various formats (PDF, DOCX, TXT, MD, CSV)
"""

import asyncio
from typing import List
from pathlib import Path

from langchain.schema import Document

try:
    from langchain_community.document_loaders import PyPDFLoader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from langchain_community.document_loaders import Docx2txtLoader
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from langchain_community.document_loaders import CSVLoader
    CSV_AVAILABLE = True
except ImportError:
    CSV_AVAILABLE = False

from utils.logger import logger


async def load_pdf(file_path: Path) -> List[Document]:
    """
    Load PDF document.

    Args:
        file_path: Path to PDF file

    Returns:
        List of LangChain Documents
    """
    try:
        if not PDF_AVAILABLE:
            logger.error("❌ PDF support not available. Install with: pip install pypdf")
            return []

        logger.info(f"📄 Loading PDF: {file_path.name}")

        loader = PyPDFLoader(str(file_path))
        documents = await asyncio.to_thread(loader.load)

        # Add metadata
        for doc in documents:
            doc.metadata['source'] = file_path.name
            doc.metadata['file_type'] = 'pdf'

        logger.info(f"✅ Loaded {len(documents)} pages from PDF")
        return documents

    except Exception as e:
        logger.error(f"❌ Error loading PDF {file_path.name}: {e}")
        return []


async def load_docx(file_path: Path) -> List[Document]:
    """
    Load DOCX document.

    Args:
        file_path: Path to DOCX file

    Returns:
        List of LangChain Documents
    """
    try:
        if not DOCX_AVAILABLE:
            logger.error("❌ DOCX support not available. Install with: pip install docx2txt")
            return []

        logger.info(f"📄 Loading DOCX: {file_path.name}")

        loader = Docx2txtLoader(str(file_path))
        documents = await asyncio.to_thread(loader.load)

        # Add metadata
        for doc in documents:
            doc.metadata['source'] = file_path.name
            doc.metadata['file_type'] = 'docx'

        logger.info(f"✅ Loaded DOCX document")
        return documents

    except Exception as e:
        logger.error(f"❌ Error loading DOCX {file_path.name}: {e}")
        return []


async def load_txt(file_path: Path) -> List[Document]:
    """
    Load TXT document.

    Args:
        file_path: Path to TXT file

    Returns:
        List of LangChain Documents
    """
    try:
        logger.info(f"📄 Loading TXT: {file_path.name}")

        content = await asyncio.to_thread(file_path.read_text, encoding='utf-8')

        doc = Document(
            page_content=content,
            metadata={
                'source': file_path.name,
                'file_type': 'txt'
            }
        )

        logger.info(f"✅ Loaded TXT document ({len(content)} chars)")
        return [doc]

    except Exception as e:
        logger.error(f"❌ Error loading TXT {file_path.name}: {e}")
        return []


async def load_markdown(file_path: Path) -> List[Document]:
    """
    Load Markdown document.

    Args:
        file_path: Path to MD file

    Returns:
        List of LangChain Documents
    """
    try:
        logger.info(f"📄 Loading Markdown: {file_path.name}")

        content = await asyncio.to_thread(file_path.read_text, encoding='utf-8')

        doc = Document(
            page_content=content,
            metadata={
                'source': file_path.name,
                'file_type': 'markdown'
            }
        )

        logger.info(f"✅ Loaded Markdown document ({len(content)} chars)")
        return [doc]

    except Exception as e:
        logger.error(f"❌ Error loading Markdown {file_path.name}: {e}")
        return []


async def load_csv(file_path: Path) -> List[Document]:
    """
    Load CSV document.

    Args:
        file_path: Path to CSV file

    Returns:
        List of LangChain Documents
    """
    try:
        if not CSV_AVAILABLE:
            logger.error("❌ CSV support not available")
            # Fallback: read as text
            return await load_txt(file_path)

        logger.info(f"📄 Loading CSV: {file_path.name}")

        loader = CSVLoader(str(file_path))
        documents = await asyncio.to_thread(loader.load)

        # Add metadata
        for doc in documents:
            doc.metadata['source'] = file_path.name
            doc.metadata['file_type'] = 'csv'

        logger.info(f"✅ Loaded {len(documents)} rows from CSV")
        return documents

    except Exception as e:
        logger.error(f"❌ Error loading CSV {file_path.name}: {e}")
        return []


async def load_document(file_path: Path) -> List[Document]:
    """
    Load document based on file extension.

    Args:
        file_path: Path to document

    Returns:
        List of LangChain Documents
    """
    extension = file_path.suffix.lower()

    loaders = {
        '.pdf': load_pdf,
        '.docx': load_docx,
        '.txt': load_txt,
        '.md': load_markdown,
        '.csv': load_csv,
    }

    loader = loaders.get(extension)

    if loader:
        return await loader(file_path)
    else:
        logger.warning(f"⚠️  Unsupported file type: {extension}")
        return []


# Export
__all__ = [
    'load_pdf',
    'load_docx',
    'load_txt',
    'load_markdown',
    'load_csv',
    'load_document',
]
