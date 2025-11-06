"""
FARADAY AI - Branding Configuration
Prvi hrvatski LLM chat sustav 🇭🇷
"""

# Application Identity
APP_NAME = "FARADAY AI"
APP_TAGLINE = "Prvi hrvatski LLM 🇭🇷"
APP_VERSION = "1.0.0"
APP_AUTHOR = "FARADAY AI Team"

# Color Scheme
COLORS = {
    "primary": "#0066CC",      # Electric blue
    "secondary": "#FF3366",    # Vibrant red (Croatian flag)
    "accent": "#00CC99",       # Teal
    "background": "#0F172A",   # Dark blue-gray
    "surface": "#1E293B",      # Lighter dark
    "text": "#F8FAFC",         # Off-white
    "text_secondary": "#94A3B8",  # Gray
    "success": "#10B981",      # Green
    "warning": "#F59E0B",      # Orange
    "error": "#EF4444",        # Red
    "info": "#3B82F6",         # Blue
}

# Welcome Message
WELCOME_MESSAGE = """
# 🇭🇷 Dobrodošli u FARADAY AI!

**Prvi hrvatski LLM chat sustav** koji kombinira najnovije AI tehnologije:

### ✨ Mogućnosti:
- 🤖 **Multi-provider LLM** (OpenAI, Anthropic, Local modeli)
- 📚 **RAG System** - Razgovarajte sa svojim dokumentima
- 🎙️ **Hrvatski TTS** - Text-to-Speech na hrvatskom jeziku
- 🤝 **AI Agenti** - Multi-step reasoning i automatizacija
- 🔍 **Web Search** - Pretraživanje interneta u realnom vremenu
- 💻 **Code Interpreter** - Izvršavanje Python koda
- 📧 **Gmail Integration** - Slanje i čitanje emailova
- 💬 **WhatsApp Integration** - WhatsApp poruke preko Twilio
- 🎨 **Artifact Generator** - Generiranje React komponenti, dokumenata, grafova

### 🚀 Kako započeti:
1. Upišite bilo koje pitanje ili naredbu
2. Koristite `/help` za popis dostupnih naredbi
3. Uploadajte dokumente za RAG pretraživanje

**Primjeri:**
- "Pretraži web za najnovije vijesti o AI"
- "Izvršite ovaj Python kod: print('Bok!')"
- "Generiraj React komponentu za login formu"
- "Pošalji email na address@example.com"
- "Pretvori ovaj tekst u govor"

Započnimo! 💪
"""

# System Prompt
SYSTEM_PROMPT = """Ti si FARADAY AI, prvi hrvatski LLM chat asistent kreiran za pružanje naprednih AI usluga na hrvatskom jeziku.

**Tvoja uloga:**
- Pružati točne i korisne odgovore na pitanja korisnika
- Koristiti dostupne alate (tools) kada je potrebno
- Biti ljubazan, profesionalan i pomagati
- Razgovarati na hrvatskom jeziku kada je to primjereno
- Biti transparentan o svojim sposobnostima i ograničenjima

**Dostupni alati:**
- RAG Search: Pretraživanje uploaded dokumenata
- Web Search: Internet pretraživanje
- Code Interpreter: Izvršavanje Python koda
- Artifact Generator: Generiranje React komponenti, dokumenata, grafova
- Gmail: Slanje i čitanje emailova
- WhatsApp: Slanje poruka
- N8N: Pokretanje automatizacijskih workflow-a
- TTS: Text-to-Speech na hrvatskom i engleskom

**Pravila:**
1. Ako korisnik uploaduje dokumente, koristi RAG search za kontekst
2. Ako trebaš trenutne informacije, koristi web search
3. Za matematičke kalkulacije ili analizu podataka, koristi code interpreter
4. Za UI komponente ili vizualizacije, koristi artifact generator
5. Uvijek objasni što radiš i zašto
6. Ako nešto ne znaš ili ne možeš, budi iskren

Komunikacija je ključna - uvijek drži korisnika informiranim o svojim akcijama!"""

# UI Configuration
UI_CONFIG = {
    "theme": "dark",
    "font_family": "Inter, system-ui, sans-serif",
    "border_radius": "8px",
    "animation_speed": "0.2s",
    "show_avatars": True,
    "enable_audio": True,
    "enable_file_upload": True,
    "max_file_size_mb": 50,
}

# Chat Settings
CHAT_CONFIG = {
    "max_message_length": 8000,
    "typing_indicator": True,
    "show_timestamps": True,
    "enable_markdown": True,
    "enable_code_highlight": True,
    "enable_latex": True,
    "default_language": "hr",
}

# Branding Assets
LOGO_PATH = "ui/assets/logo.png"
FAVICON_PATH = "ui/assets/favicon.ico"

# Footer
FOOTER_TEXT = f"© 2025 {APP_NAME} | Powered by LangChain, Chainlit & OpenAI | Made with ❤️ in Croatia 🇭🇷"

# Help Text
HELP_TEXT = """
## 📖 FARADAY AI - Pomoć

### Osnovne naredbe:
- `/help` - Prikaži ovu pomoć
- `/clear` - Obriši povijest razgovora
- `/new` - Započni novi razgovor
- `/settings` - Postavke sustava

### Korištenje alata:

**RAG (Dokument pretraživanje):**
Upload dokumente (PDF, DOCX, TXT) i postavi pitanja o njima.

**Web Search:**
"Pretraži web za..." ili "Što je najnovije o..."

**Code Interpreter:**
"Izvršite Python kod: ..." ili "Izračunaj..."

**Artifact Generator:**
"Generiraj React komponentu za..." ili "Napravi prezentaciju o..."

**Email (Gmail):**
"Pošalji email na [email] sa sadržajem..."

**WhatsApp:**
"Pošalji WhatsApp poruku na +385... sa tekstom..."

### Podrška:
Za više informacija pogledajte README.md ili kontaktirajte support@faraday-ai.hr
"""

# Export all
__all__ = [
    'APP_NAME',
    'APP_TAGLINE',
    'APP_VERSION',
    'APP_AUTHOR',
    'COLORS',
    'WELCOME_MESSAGE',
    'SYSTEM_PROMPT',
    'UI_CONFIG',
    'CHAT_CONFIG',
    'LOGO_PATH',
    'FAVICON_PATH',
    'FOOTER_TEXT',
    'HELP_TEXT',
]
