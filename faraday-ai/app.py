"""
FARADAY AI - Main Chainlit Application
Prvi hrvatski LLM chat sustav 🇭🇷
"""

import asyncio
from pathlib import Path
from typing import Optional

import chainlit as cl

# Import config
from config.branding import (
    APP_NAME, APP_TAGLINE, WELCOME_MESSAGE, SYSTEM_PROMPT,
    HELP_TEXT, COLORS, UI_CONFIG, CHAT_CONFIG
)
from config.settings import settings

# Import engines
from engines.llm_engine import get_llm_engine
from engines.rag_engine import get_rag_engine
from engines.tts_engine import get_tts_engine
from engines.agent_engine import get_agent_engine

# Import tools
from tools.function_registry import function_registry
from tools import web_search, execute_code, generate_artifact, calculator

# Import connectors
from connectors.gmail_connector import get_gmail_connector
from connectors.whatsapp_connector import get_whatsapp_connector
from connectors.n8n_connector import get_n8n_connector

# Import utils
from utils.logger import logger, setup_file_logging


# Setup file logging
setup_file_logging(settings.logging.log_file, settings.logging.level)

# Print startup banner
logger.info("="*60)
logger.info(f"🇭🇷 {APP_NAME} - {APP_TAGLINE}")
logger.info("="*60)

# Validate configuration
validation = settings.validate()
settings.print_status()

if not validation['valid']:
    logger.error("❌ Configuration validation failed! Please fix the issues above.")

# Initialize engines
llm_engine = get_llm_engine()
rag_engine = get_rag_engine()
tts_engine = get_tts_engine()
agent_engine = get_agent_engine()

logger.info("✅ All engines initialized")


@cl.on_chat_start
async def start():
    """
    Called when a new chat session starts.
    """
    try:
        logger.info("🚀 New chat session started")

        # Display welcome message
        await cl.Message(
            content=WELCOME_MESSAGE,
            author=APP_NAME
        ).send()

        # Initialize session variables
        cl.user_session.set("message_history", [])
        cl.user_session.set("rag_enabled", False)

        # Try to load existing vectorstore
        logger.info("📚 Checking for existing RAG vectorstore...")
        vectorstore_loaded = await rag_engine.load_vectorstore()

        if vectorstore_loaded:
            await cl.Message(
                content="✅ **RAG System Ready!** Documents loaded and ready for search.",
                author="System"
            ).send()
            cl.user_session.set("rag_enabled", True)
        else:
            # Check if there are documents to load
            doc_count = await rag_engine.load_documents_from_directory()
            if doc_count > 0:
                await cl.Message(
                    content=f"✅ **RAG System Initialized!** Loaded {doc_count} documents.",
                    author="System"
                ).send()
                cl.user_session.set("rag_enabled", True)

        # Initialize connectors if needed
        if settings.connectors.gmail_enabled:
            logger.info("📧 Gmail connector available")

        if settings.connectors.whatsapp_enabled:
            logger.info("💬 WhatsApp connector available")

        if settings.connectors.n8n_enabled:
            logger.info("🔗 N8N connector available")

        logger.info("✅ Chat session initialized")

    except Exception as e:
        logger.error(f"❌ Error in chat start: {e}")
        await cl.Message(
            content=f"⚠️ Error during initialization: {str(e)}",
            author="System"
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    Main message handler.
    """
    try:
        user_message = message.content
        logger.info(f"💬 User message: {user_message[:100]}...")

        # Get message history
        message_history = cl.user_session.get("message_history", [])
        rag_enabled = cl.user_session.get("rag_enabled", False)

        # Check for special commands
        if user_message.startswith("/"):
            await handle_command(user_message)
            return

        # Check if RAG search is needed
        rag_context = ""
        if rag_enabled and any(keyword in user_message.lower() for keyword in ["dokument", "document", "file", "pronađi", "traži", "search"]):
            logger.info("🔍 Performing RAG search...")

            msg = cl.Message(content="🔍 Pretraživanje dokumenata...", author="System")
            await msg.send()

            rag_context = await rag_engine.get_context_for_query(user_message)

            if rag_context and rag_context != "No relevant documents found.":
                await msg.update(content=f"✅ Pronađeni relevantni dokumenti!\n\n")
                logger.info("✅ RAG context retrieved")
            else:
                await msg.remove()

        # Build prompt with RAG context
        if rag_context:
            enhanced_prompt = f"""Kontekst iz dokumenata:
{rag_context}

---

Pitanje korisnika: {user_message}

Koristi gornji kontekst iz dokumenata da odgovoriš na pitanje. Ako kontekst nije relevantan, odgovori na osnovu svog znanja."""
        else:
            enhanced_prompt = user_message

        # Add system prompt
        system_prompt = SYSTEM_PROMPT

        # Stream LLM response
        msg = cl.Message(content="", author=APP_NAME)
        await msg.send()

        full_response = ""

        async for chunk in llm_engine.generate(
            prompt=enhanced_prompt,
            system_prompt=system_prompt,
            stream=True
        ):
            full_response += chunk
            await msg.stream_token(chunk)

        await msg.update()

        # Save to history
        message_history.append({"role": "user", "content": user_message})
        message_history.append({"role": "assistant", "content": full_response})
        cl.user_session.set("message_history", message_history[-10:])  # Keep last 10 messages

        # Generate TTS if enabled
        if tts_engine.is_available() and CHAT_CONFIG.get("default_language") == "hr":
            # Only generate TTS for shorter responses
            if len(full_response) < 500:
                logger.info("🎙️ Generating TTS...")
                audio_path = await tts_engine.synthesize_speech(
                    full_response[:300],  # Limit length
                    language="hr"
                )

                if audio_path:
                    # Note: Chainlit audio support
                    logger.info(f"✅ TTS generated: {audio_path}")

        logger.info("✅ Response sent")

    except Exception as e:
        logger.error(f"❌ Error in message handler: {e}")
        await cl.Message(
            content=f"⚠️ Dogodila se greška: {str(e)}",
            author="System"
        ).send()


async def handle_command(command: str):
    """
    Handle special commands.
    """
    try:
        cmd = command.lower().strip()

        if cmd == "/help":
            await cl.Message(content=HELP_TEXT, author="System").send()

        elif cmd == "/clear":
            cl.user_session.set("message_history", [])
            await cl.Message(content="✅ Povijest razgovora obrisana.", author="System").send()

        elif cmd == "/status":
            # Show system status
            status_msg = f"""
## 📊 Status Sustava

**LLM Provider:** {llm_engine.get_provider()}
**Model:** {llm_engine.get_model_name()}

**RAG:** {'✅ Aktivan' if cl.user_session.get("rag_enabled") else '❌ Neaktivan'}
**TTS:** {'✅ Dostupan' if tts_engine.is_available() else '❌ Nedostupan'}
**Agenti:** {'✅ Aktivni' if agent_engine.enabled else '❌ Neaktivni'}

**Dostupni alati:**
{', '.join(settings.get_enabled_tools())}

**Konekcije:**
- Gmail: {'✅' if settings.connectors.gmail_enabled else '❌'}
- WhatsApp: {'✅' if settings.connectors.whatsapp_enabled else '❌'}
- N8N: {'✅' if settings.connectors.n8n_enabled else '❌'}
"""
            await cl.Message(content=status_msg, author="System").send()

        elif cmd == "/tools":
            # List available tools
            tools_list = function_registry.list_functions()
            tools_msg = f"""
## 🔧 Dostupni Alati

{', '.join(tools_list)}

Koristite `/help` za detalje o svakom alatu.
"""
            await cl.Message(content=tools_msg, author="System").send()

        elif cmd.startswith("/rag"):
            # RAG commands
            if cmd == "/rag reload":
                await cl.Message(content="🔄 Ponovno učitavanje dokumenata...", author="System").send()
                doc_count = await rag_engine.load_documents_from_directory()
                await cl.Message(
                    content=f"✅ Učitano {doc_count} dokumenata.",
                    author="System"
                ).send()
                cl.user_session.set("rag_enabled", doc_count > 0)

        else:
            await cl.Message(
                content=f"⚠️ Nepoznata naredba: {command}\n\nKoristite `/help` za popis naredbi.",
                author="System"
            ).send()

    except Exception as e:
        logger.error(f"❌ Command error: {e}")
        await cl.Message(
            content=f"⚠️ Greška kod izvršavanja naredbe: {str(e)}",
            author="System"
        ).send()


@cl.on_chat_end
async def end():
    """
    Called when chat session ends.
    """
    logger.info("👋 Chat session ended")


# File upload handler
@cl.on_file_upload
async def handle_file_upload(files: list):
    """
    Handle file uploads for RAG.
    """
    try:
        logger.info(f"📎 Files uploaded: {len(files)}")

        uploaded_files = []
        total_chunks = 0

        for file in files:
            # Save file
            file_path = settings.documents_dir / file.name
            file_path.write_bytes(file.content)

            # Load into RAG
            chunks = await rag_engine.load_document(file_path)
            total_chunks += chunks

            uploaded_files.append(file.name)

            logger.info(f"✅ File uploaded and processed: {file.name}")

        # Enable RAG
        cl.user_session.set("rag_enabled", True)

        await cl.Message(
            content=f"""✅ **Datoteke učitane!**

**Učitano:** {', '.join(uploaded_files)}
**Ukupno dijelova:** {total_chunks}

Sada možete postavljati pitanja o uploadanim dokumentima!""",
            author="System"
        ).send()

    except Exception as e:
        logger.error(f"❌ File upload error: {e}")
        await cl.Message(
            content=f"⚠️ Greška kod uploadanja datoteka: {str(e)}",
            author="System"
        ).send()


# Run the app
if __name__ == "__main__":
    logger.info("🚀 Starting FARADAY AI...")
    logger.info("Use: chainlit run app.py")
