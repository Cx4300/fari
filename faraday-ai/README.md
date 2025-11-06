# 🇭🇷 FARADAY AI

**Prvi hrvatski LLM chat sustav**

Moderan AI chat sustav kreiran od nule s podrškom za:
- 🤖 Multi-provider LLM (OpenAI, Anthropic, Local modeli)
- 📚 RAG (Retrieval-Augmented Generation) sa FAISS
- 🎙️ Hrvatski TTS (Text-to-Speech) sa Coqui
- 🤝 AI Agenti za multi-step reasoning
- 🔧 Function calling i tool orchestration
- 📧 Gmail, WhatsApp, N8N integracije

---

## ✨ Mogućnosti

### 🤖 Multi-Provider LLM
- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **Anthropic** (Claude 3.5 Sonnet)
- **Local Models** (Unsloth, GGUF)
- Streaming responses
- Function calling support

### 📚 RAG System
- FAISS vector store
- Multilingual embeddings (paraphrase-multilingual-mpnet-base-v2)
- Support za PDF, DOCX, TXT, MD, CSV
- Semantic search
- Drag & drop file upload

### 🎙️ Hrvatski TTS
- Coqui TTS engine
- Hrvatski i engleski govor
- Streaming audio
- Auto-generiranje govora za odgovore

### 🔧 Tools & Function Calling
- **Web Search** - Google, Bing, DuckDuckGo
- **Code Interpreter** - Siguran Python sandbox
- **Artifact Generator** - React komponente, dokumenti, grafovi
- **Calculator** - Matematičke operacije
- Extensible function registry

### 🤝 AI Agenti
- Multi-step planning
- Tool orchestration
- ReAct (Reasoning + Acting) pattern
- Self-reflection

### 🔗 Connectors
- **Gmail** - Slanje i čitanje emailova
- **WhatsApp** - Twilio integracija
- **N8N** - Workflow automatizacija

---

## 🚀 Quick Start

### Preduvjeti

- Python 3.9+
- pip
- Git

### Instalacija

```bash
# 1. Clone repository
git clone https://github.com/your-username/faraday-ai.git
cd faraday-ai

# 2. Run installation script
bash install.sh

# 3. Edit .env file with your API keys
nano .env

# 4. Run FARADAY AI
source venv/bin/activate
chainlit run app.py
```

### Konfiguracija

Uredite `.env` file:

```bash
# Minimum required
OPENAI_API_KEY=sk-your-key-here
PRIMARY_LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4

# Optional
ENABLE_TTS=true
ENABLED_TOOLS=web_search,code_interpreter,calculator,artifact_generator,rag
```

---

## 📖 Dokumentacija

### Struktura Projekta

```
faraday-ai/
├── config/
│   ├── branding.py          # Brand config
│   └── settings.py          # System settings
├── engines/
│   ├── llm_engine.py        # LLM engine
│   ├── rag_engine.py        # RAG engine
│   ├── tts_engine.py        # TTS engine
│   └── agent_engine.py      # Agent engine
├── tools/
│   ├── function_registry.py # Function calling
│   ├── web_search.py        # Web search
│   ├── code_interpreter.py  # Code execution
│   ├── artifact_generator.py# Artifact generation
│   └── calculator.py        # Calculator
├── connectors/
│   ├── gmail_connector.py   # Gmail
│   ├── whatsapp_connector.py# WhatsApp
│   └── n8n_connector.py     # N8N
├── auth/
│   ├── auth_manager.py      # Authentication
│   └── user_database.py     # User DB
├── utils/
│   ├── embeddings.py        # Embeddings
│   ├── document_loader.py   # Document loading
│   ├── streaming_utils.py   # Streaming
│   └── logger.py            # Logging
├── data/
│   ├── documents/           # RAG documents
│   ├── faiss_index/         # Vector store
│   └── artifacts/           # Generated artifacts
├── app.py                   # Main Chainlit app
├── requirements.txt
├── .env.example
└── install.sh
```

### Korištenje

#### Chat Commands

```
/help       - Prikaži pomoć
/clear      - Obriši povijest
/status     - Status sustava
/tools      - Lista alata
/rag reload - Ponovno učitaj dokumente
```

#### RAG (Document Search)

1. Upload dokumente (PDF, DOCX, TXT)
2. Postavi pitanja o dokumentima
3. Sistem automatski pronalazi relevantne informacije

#### Function Calling

Sistem automatski poziva funkcije kada je potrebno:

```
"Pretraži web za najnovije vijesti o AI"
→ Poziva web_search()

"Izvršite: print(2 + 2)"
→ Poziva execute_code()

"Generiraj React login komponentu"
→ Poziva generate_artifact()
```

---

## 🔧 Konfiguracija

### LLM Config

```python
# config/settings.py
PRIMARY_LLM_PROVIDER = "openai"  # openai, anthropic, local
OPENAI_MODEL = "gpt-4"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2000
```

### RAG Config

```python
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5
```

### TTS Config

```python
ENABLE_TTS = True
TTS_MODEL_HR = "tts_models/hr/cv/vits"
TTS_DEFAULT_LANGUAGE = "hr"
```

### Tools Config

```python
ENABLED_TOOLS = "web_search,code_interpreter,calculator,artifact_generator,rag"
```

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_llm_engine.py

# With coverage
pytest --cov=. tests/
```

---

## 📝 Development

### Adding New Tools

1. Create tool file in `tools/`
2. Use `@register_function` decorator
3. Add to `ENABLED_TOOLS` in `.env`

Example:

```python
from tools.function_registry import register_function

@register_function(
    name="my_tool",
    description="My custom tool",
    parameters={
        "type": "object",
        "properties": {
            "input": {"type": "string"}
        }
    }
)
async def my_tool(input: str) -> dict:
    # Implementation
    return {"result": input.upper()}
```

### Adding New Connectors

1. Create connector file in `connectors/`
2. Implement connector class
3. Add configuration to `settings.py`

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Credits

Built with:
- [Chainlit](https://chainlit.io/) - Chat UI framework
- [LangChain](https://langchain.com/) - LLM framework
- [OpenAI](https://openai.com/) - GPT models
- [Anthropic](https://anthropic.com/) - Claude models
- [Coqui TTS](https://github.com/coqui-ai/TTS) - Text-to-Speech
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search

---

## 📞 Contact

- Website: https://faraday-ai.hr
- Email: info@faraday-ai.hr
- GitHub: https://github.com/your-username/faraday-ai

---

**Made with ❤️ in Croatia 🇭🇷**
