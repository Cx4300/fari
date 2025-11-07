# 🚀 POKRETANJE FARADAY AI

## Trenutni status instalacije

Instalacija dependencies je u tijeku. Ovo je normalno i može potrajati 5-10 minuta zbog velikih paketa (PyTorch, TTS, Transformers).

---

## ✅ Opcija 1: Čekanje na punu instalaciju

**Što se instalira:**
- ✅ Chainlit (UI framework)
- ✅ OpenAI & Anthropic klijenti
- ✅ LangChain (RAG)
- ⏳ PyTorch (2GB+) - veliki paket
- ⏳ Transformers (HuggingFace)
- ⏳ Coqui TTS (hrvatski govor)
- ⏳ FAISS (vector search)
- ⏳ spaCy, gruut (NLP)

**Provjeri status:**
```bash
cd ~/fari/faraday-ai
source venv/bin/activate
pip list | grep chainlit
```

Ako je chainlit instaliran, možeš pokrenuti!

---

## 🚀 Opcija 2: Minimalna instalacija (BRZA)

Pokreni bez TTS-a i ML biblioteka:

```bash
cd ~/fari/faraday-ai

# Kreiraj novi venv
python3 -m venv venv-minimal
source venv-minimal/bin/activate

# Instaliraj minimalne dependencies (< 2 min)
pip install -r requirements-minimal.txt

# Pokreni aplikaciju
python -m chainlit run app.py --host 0.0.0.0 --port 8000
```

**Napomena:** RAG, TTS i neki alati neće raditi, ali LLM chat će raditi!

---

## 📋 Pokretanje nakon završetka instalacije

```bash
cd ~/fari/faraday-ai
source venv/bin/activate

# Provjeri je li chainlit instaliran
python -c "import chainlit; print('✅ Chainlit OK')"

# Dodaj API key u .env
nano .env
# Zamijeni: OPENAI_API_KEY=sk-test-key-please-replace
# Sa: OPENAI_API_KEY=sk-your-real-key-here

# Pokreni aplikaciju
python -m chainlit run app.py --host 0.0.0.0 --port 8000
```

---

## 🌐 Pristup aplikaciji

Nakon pokretanja, otvori browser na:

**Lokalno:**
```
http://localhost:8000
```

**Sa druge mašine (ako je host 0.0.0.0):**
```
http://YOUR_IP_ADDRESS:8000
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'chainlit'"

Instalacija još nije završena. Pričekaj ili koristi minimal install.

### "OpenAI API key missing"

Dodaj pravi API key u `.env`:
```bash
nano .env
# Promijeni:
OPENAI_API_KEY=sk-your-real-openai-key-here
```

### Port 8000 zauzet

Koristi drugi port:
```bash
python -m chainlit run app.py --port 8001
```

### Permission denied

```bash
chmod +x install.sh
```

---

## 📊 Provjeri što je instalirano

```bash
source venv/bin/activate
pip list | grep -E "chainlit|openai|langchain|torch|TTS"
```

---

## 🔄 Restart aplikacije

```bash
# Zaustavi (Ctrl+C)
# Ponovno pokreni:
source venv/bin/activate
python -m chainlit run app.py
```

---

## 📝 Logovi

Logovi se spremaju u:
```
logs/faraday-ai.log
```

Prati logove:
```bash
tail -f logs/faraday-ai.log
```

---

## ✅ Sve je spremno kada vidiš:

```
============================================================
🇭🇷 FARADAY AI - Prvi hrvatski LLM
============================================================

✅ Configuration is valid!
✅ All engines initialized
🚀 New chat session started
```

Tada možeš otvoriti browser i početi koristiti FARADAY AI! 🎉
