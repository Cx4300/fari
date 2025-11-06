# 🚀 FARADAY AI - Quick Start Guide

Brze upute za pokretanje FARADAY AI sustava u 5 minuta!

---

## 📋 Prije početka

Provjerite imate li:
- ✅ Python 3.9 ili noviji
- ✅ Git
- ✅ OpenAI API key (https://platform.openai.com/api-keys)

---

## 🎯 Instalacija u 3 koraka

### Korak 1: Clone i Install

```bash
# Clone repository
git clone https://github.com/your-username/faraday-ai.git
cd faraday-ai

# Pokreni instalaciju
bash install.sh
```

Instalacijski script će:
- ✅ Provjeriti Python verziju
- ✅ Kreirati virtual environment
- ✅ Instalirati sve dependencies
- ✅ Kreirati direktorije
- ✅ Napraviti .env file iz .env.example

⏱️ **Vrijeme trajanja:** 3-5 minuta

---

### Korak 2: Konfiguriraj API Keys

Otvori `.env` file:

```bash
nano .env
```

Dodaj svoj OpenAI API key:

```bash
# Minimum required
OPENAI_API_KEY=sk-your-actual-key-here
PRIMARY_LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4

# Optional (za dodatne funkcionalnosti)
ENABLE_TTS=true
ENABLED_TOOLS=web_search,code_interpreter,calculator,artifact_generator,rag
```

💡 **Tip:** Za testiranje možete koristiti `gpt-3.5-turbo` umjesto `gpt-4` (jeftinije)

---

### Korak 3: Pokreni FARADAY AI

```bash
# Aktiviraj virtual environment
source venv/bin/activate

# Pokreni aplikaciju
chainlit run app.py
```

Otvori browser na: **http://localhost:8000**

🎉 **Gotovo!** FARADAY AI je pokrenut!

---

## 💬 Prvi koraci

### 1. Testni razgovor

Probaj pisati:
```
Bok! Kako možeš pomoći?
```

### 2. Probaj RAG (Document Search)

**Upload dokument:**
1. Klikni na file upload ikonu
2. Upload PDF, DOCX ili TXT file
3. Postavi pitanje o dokumentu:

```
Što piše u dokumentu o AI?
```

### 3. Probaj Code Interpreter

```
Izvršite Python kod: print("Bok FARADAY!")
```

### 4. Probaj Web Search

```
Pretraži web za najnovije vijesti o umjetnoj inteligenciji
```

### 5. Probaj Artifact Generator

```
Generiraj React komponentu za login formu
```

---

## 🔧 Korisne naredbe

### Chat Commands

```
/help       - Prikaži pomoć
/status     - Status sustava
/clear      - Obriši povijest razgovora
/tools      - Lista dostupnih alata
/rag reload - Ponovno učitaj RAG dokumente
```

---

## ⚙️ Dodatna konfiguracija

### Omogući TTS (Hrvatski govor)

U `.env`:
```bash
ENABLE_TTS=true
TTS_DEFAULT_LANGUAGE=hr
```

TTS modeli će se skinuti automatski pri prvom korištenju.

### Dodaj Web Search

Za DuckDuckGo (besplatno):
```bash
WEB_SEARCH_ENGINE=duckduckgo
```

Za Google/Bing (treba API key):
```bash
WEB_SEARCH_ENGINE=google
WEB_SEARCH_API_KEY=your-api-key
```

### Omogući Agente

```bash
ENABLE_AGENTS=true
AGENT_MAX_ITERATIONS=10
```

---

## 📁 Upload Dokumenata za RAG

### Metoda 1: Drag & Drop u UI

Jednostavno drag & drop PDF, DOCX ili TXT file u chat.

### Metoda 2: Kopiraj u data/documents/

```bash
cp mojdokument.pdf data/documents/
```

Zatim u chatu:
```
/rag reload
```

---

## 🐛 Troubleshooting

### Problem: "OpenAI API key missing"

**Rješenje:** Provjeri `.env` file:
```bash
cat .env | grep OPENAI_API_KEY
```
Ako je prazan, dodaj key.

### Problem: "Module not found"

**Rješenje:** Reinstaliraj dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: TTS modeli se ne skidaju

**Rješenje:** Ručno skini model:
```bash
python -c "from TTS.api import TTS; TTS('tts_models/hr/cv/vits')"
```

### Problem: Port 8000 already in use

**Rješenje:** Koristi drugi port:
```bash
chainlit run app.py --port 8001
```

---

## 📚 Dodatni resursi

- **Full dokumentacija:** README.md
- **OpenAI API keys:** https://platform.openai.com/api-keys
- **Chainlit docs:** https://docs.chainlit.io/
- **LangChain docs:** https://python.langchain.com/

---

## 🎓 Primjeri korištenja

###Ример 1: Analiza dokumenta

```
1. Upload PDF dokument
2. "Sažmi ovaj dokument u 3 ključne točke"
3. "Koji su najvažniji zaključci?"
```

### Primer 2: Code execution

```
"Izračunaj prvih 10 Fibonacci brojeva pomoću Python koda"
```

### Primer 3: Web + RAG

```
1. Upload company document
2. "Pretraži web za konkurente tvrtke spomenute u dokumentu"
```

### Primer 4: Multi-step Agent

```
"Istraži temu AI u zdravstvu, napravi sažetak i generiraj презентацију"
```

---

## 🚀 Napredne opcije

### Local Models (Unsloth)

Ako želiš koristiti lokalne modele:

```bash
# Install Unsloth
pip install "unsloth @ git+https://github.com/unslothai/unsloth.git"

# Update .env
PRIMARY_LLM_PROVIDER=local
LOCAL_MODEL=path/to/your/model
```

### Gmail Integration

1. Skini Gmail credentials JSON
2. Kopiraj u `credentials/gmail_credentials.json`
3. Update `.env`:
```bash
ENABLED_CONNECTORS=gmail
```

### N8N Workflows

```bash
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/...
ENABLED_CONNECTORS=n8n
```

---

## ✅ Checklist

Prije production deploya:

- [ ] Promijeni `JWT_SECRET_KEY` u `.env`
- [ ] Omogući `AUTH_ENABLED=true`
- [ ] Postavi production database (ne SQLite)
- [ ] Setup reverse proxy (nginx)
- [ ] Omogući HTTPS
- [ ] Setup backup za data/faiss_index/
- [ ] Configure rate limiting
- [ ] Setup monitoring (logs)

---

## 🤝 Podrška

Imaš pitanja?

1. Provjeri README.md
2. Provjeri GitHub Issues
3. Kontaktiraj: info@faraday-ai.hr

---

**Sretno! 🇭🇷**

**Made with ❤️ in Croatia**
