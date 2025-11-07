"""
FARADAY AI - Minimal Chainlit Application
Minimal verzija bez RAG/TTS/Agent dependencies
"""

import chainlit as cl
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# Welcome message
WELCOME = """
# 🇭🇷 Dobrodošli u FARADAY AI!

**Prvi hrvatski LLM chat sustav** (Minimal Mode)

✅ **Aktivno:**
- OpenAI GPT-4 Chat
- Streaming responses

⚠️ **Deaktivirano** (instaliraj dependencies):
- RAG (Document Search)
- TTS (Hrvatski govor)
- AI Agenti
- Tools (web search, code, artifacts)

**Dodajte pravi API key u `.env`:**
```
OPENAI_API_KEY=sk-your-real-key-here
```

Započnimo! 💬
"""


@cl.on_chat_start
async def start():
    """Start chat session"""
    await cl.Message(content=WELCOME, author="FARADAY AI").send()
    cl.user_session.set("messages", [])


@cl.on_message
async def main(message: cl.Message):
    """Handle messages"""
    try:
        # Get message history
        messages = cl.user_session.get("messages", [])

        # Add user message
        messages.append({"role": "user", "content": message.content})

        # Stream response from OpenAI
        msg = cl.Message(content="", author="FARADAY AI")
        await msg.send()

        full_response = ""

        stream = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=2000
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                await msg.stream_token(chunk.choices[0].delta.content)

        await msg.update()

        # Save to history
        messages.append({"role": "assistant", "content": full_response})
        cl.user_session.set("messages", messages[-10:])  # Keep last 10

    except Exception as e:
        await cl.Message(
            content=f"⚠️ Greška: {str(e)}\n\nProvjerite OPENAI_API_KEY u .env",
            author="System"
        ).send()


if __name__ == "__main__":
    print("🚀 FARADAY AI - Minimal Mode")
    print("Run: chainlit run app-minimal.py")
