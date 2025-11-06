"""
FARADAY AI - Settings Configuration
Centralna konfiguracija za sve funkcionalnosti
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
FAISS_INDEX_DIR = DATA_DIR / "faiss_index"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, DOCUMENTS_DIR, FAISS_INDEX_DIR, ARTIFACTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class LLMConfig(BaseModel):
    """LLM Engine Configuration"""

    # Primary LLM Provider (openai, anthropic, local)
    primary_provider: str = Field(default_factory=lambda: os.getenv("PRIMARY_LLM_PROVIDER", "openai"))

    # Model names
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4"))
    anthropic_model: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"))
    local_model: str = Field(default_factory=lambda: os.getenv("LOCAL_MODEL", "gpt-oss-20b"))

    # API Keys
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))

    # Generation parameters
    temperature: float = Field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.7")))
    max_tokens: int = Field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "2000")))
    top_p: float = Field(default_factory=lambda: float(os.getenv("LLM_TOP_P", "1.0")))
    frequency_penalty: float = Field(default_factory=lambda: float(os.getenv("LLM_FREQUENCY_PENALTY", "0.0")))
    presence_penalty: float = Field(default_factory=lambda: float(os.getenv("LLM_PRESENCE_PENALTY", "0.0")))

    # Streaming
    enable_streaming: bool = Field(default_factory=lambda: os.getenv("LLM_ENABLE_STREAMING", "true").lower() == "true")

    # Function calling
    enable_function_calling: bool = Field(default_factory=lambda: os.getenv("ENABLE_FUNCTION_CALLING", "true").lower() == "true")


class RAGConfig(BaseModel):
    """RAG Engine Configuration"""

    # Embedding model
    embedding_model: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"))

    # Chunking parameters
    chunk_size: int = Field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000")))
    chunk_overlap: int = Field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200")))

    # Search parameters
    top_k_results: int = Field(default_factory=lambda: int(os.getenv("TOP_K_RESULTS", "5")))
    similarity_threshold: float = Field(default_factory=lambda: float(os.getenv("SIMILARITY_THRESHOLD", "0.7")))

    # Vector store
    vector_store_path: Path = FAISS_INDEX_DIR

    # Document processing
    supported_extensions: List[str] = [".pdf", ".docx", ".txt", ".md", ".csv"]
    max_document_size_mb: int = 50


class TTSConfig(BaseModel):
    """Text-to-Speech Configuration"""

    # TTS models
    tts_model_hr: str = Field(default_factory=lambda: os.getenv("TTS_MODEL_HR", "tts_models/hr/cv/vits"))
    tts_model_en: str = Field(default_factory=lambda: os.getenv("TTS_MODEL_EN", "tts_models/en/ljspeech/tacotron2-DDC"))

    # Default language
    default_language: str = Field(default_factory=lambda: os.getenv("TTS_DEFAULT_LANGUAGE", "hr"))

    # Audio settings
    sample_rate: int = 22050
    enable_streaming: bool = True
    output_format: str = "wav"

    # Enable/disable TTS
    enabled: bool = Field(default_factory=lambda: os.getenv("ENABLE_TTS", "true").lower() == "true")


class AgentConfig(BaseModel):
    """Agent Engine Configuration"""

    # Enable agents
    enabled: bool = Field(default_factory=lambda: os.getenv("ENABLE_AGENTS", "true").lower() == "true")

    # Agent parameters
    max_iterations: int = Field(default_factory=lambda: int(os.getenv("AGENT_MAX_ITERATIONS", "10")))
    enable_reflection: bool = True
    enable_planning: bool = True

    # Timeout
    timeout_seconds: int = 300


class ToolsConfig(BaseModel):
    """Tools Configuration"""

    # Enabled tools (comma-separated in .env)
    enabled_tools: List[str] = Field(
        default_factory=lambda: os.getenv("ENABLED_TOOLS", "web_search,code_interpreter,calculator,artifact_generator,rag").split(",")
    )

    # Web Search
    web_search_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("WEB_SEARCH_API_KEY"))
    web_search_engine: str = Field(default_factory=lambda: os.getenv("WEB_SEARCH_ENGINE", "google"))  # google, bing, duckduckgo

    # Code Interpreter
    code_interpreter_timeout: int = 30
    code_interpreter_max_output_length: int = 10000

    # Calculator
    calculator_precision: int = 10


class ConnectorsConfig(BaseModel):
    """Connectors Configuration"""

    # Gmail
    gmail_enabled: bool = Field(default_factory=lambda: "gmail" in os.getenv("ENABLED_CONNECTORS", "").split(","))
    gmail_credentials_path: Path = BASE_DIR / "credentials" / "gmail_credentials.json"
    gmail_token_path: Path = BASE_DIR / "credentials" / "gmail_token.json"

    # WhatsApp (Twilio)
    whatsapp_enabled: bool = Field(default_factory=lambda: "whatsapp" in os.getenv("ENABLED_CONNECTORS", "").split(","))
    twilio_account_sid: Optional[str] = Field(default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID"))
    twilio_auth_token: Optional[str] = Field(default_factory=lambda: os.getenv("TWILIO_AUTH_TOKEN"))
    twilio_whatsapp_number: Optional[str] = Field(default_factory=lambda: os.getenv("TWILIO_WHATSAPP_NUMBER"))

    # N8N
    n8n_enabled: bool = Field(default_factory=lambda: "n8n" in os.getenv("ENABLED_CONNECTORS", "").split(","))
    n8n_webhook_url: Optional[str] = Field(default_factory=lambda: os.getenv("N8N_WEBHOOK_URL"))
    n8n_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("N8N_API_KEY"))


class AuthConfig(BaseModel):
    """Authentication Configuration"""

    # Enable authentication
    enabled: bool = Field(default_factory=lambda: os.getenv("AUTH_ENABLED", "false").lower() == "true")

    # Database
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/users.db"))

    # JWT
    jwt_secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", "faraday-ai-secret-key-change-in-production"))
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Session
    session_timeout_minutes: int = 60


class LoggingConfig(BaseModel):
    """Logging Configuration"""

    # Log level
    level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Log file
    log_file: Path = LOGS_DIR / "faraday-ai.log"

    # Log rotation
    rotation: str = "500 MB"
    retention: str = "10 days"

    # Format
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"


class Settings:
    """Main Settings Class"""

    def __init__(self):
        self.llm = LLMConfig()
        self.rag = RAGConfig()
        self.tts = TTSConfig()
        self.agent = AgentConfig()
        self.tools = ToolsConfig()
        self.connectors = ConnectorsConfig()
        self.auth = AuthConfig()
        self.logging = LoggingConfig()

        # Paths
        self.base_dir = BASE_DIR
        self.data_dir = DATA_DIR
        self.documents_dir = DOCUMENTS_DIR
        self.faiss_index_dir = FAISS_INDEX_DIR
        self.artifacts_dir = ARTIFACTS_DIR
        self.logs_dir = LOGS_DIR

    def get_enabled_tools(self) -> List[str]:
        """Get list of enabled tools"""
        return [tool.strip() for tool in self.tools.enabled_tools if tool.strip()]

    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a specific tool is enabled"""
        return tool_name in self.get_enabled_tools()

    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        warnings = []

        # Check API keys
        if self.llm.primary_provider == "openai" and not self.llm.openai_api_key:
            issues.append("❌ OpenAI API key is missing (PRIMARY_LLM_PROVIDER=openai)")

        if self.llm.primary_provider == "anthropic" and not self.llm.anthropic_api_key:
            issues.append("❌ Anthropic API key is missing (PRIMARY_LLM_PROVIDER=anthropic)")

        # Check tools
        if "web_search" in self.get_enabled_tools() and not self.tools.web_search_api_key:
            warnings.append("⚠️  Web search is enabled but API key is missing")

        if self.connectors.whatsapp_enabled and not self.connectors.twilio_account_sid:
            warnings.append("⚠️  WhatsApp connector is enabled but Twilio credentials are missing")

        if self.connectors.gmail_enabled and not self.connectors.gmail_credentials_path.exists():
            warnings.append("⚠️  Gmail connector is enabled but credentials file is missing")

        # Check directories
        for directory in [self.data_dir, self.documents_dir, self.faiss_index_dir, self.artifacts_dir]:
            if not directory.exists():
                warnings.append(f"⚠️  Directory does not exist: {directory}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }

    def print_status(self):
        """Print configuration status"""
        print("\n" + "="*60)
        print("⚙️  FARADAY AI - Configuration Status")
        print("="*60)

        validation = self.validate()

        print(f"\n🤖 LLM Provider: {self.llm.primary_provider}")
        print(f"📚 RAG Enabled: {self.is_tool_enabled('rag')}")
        print(f"🎙️  TTS Enabled: {self.tts.enabled}")
        print(f"🤝 Agents Enabled: {self.agent.enabled}")
        print(f"🔧 Enabled Tools: {', '.join(self.get_enabled_tools())}")

        if validation['warnings']:
            print("\n⚠️  Warnings:")
            for warning in validation['warnings']:
                print(f"  {warning}")

        if validation['issues']:
            print("\n❌ Issues:")
            for issue in validation['issues']:
                print(f"  {issue}")
        else:
            print("\n✅ Configuration is valid!")

        print("="*60 + "\n")


# Global settings instance
settings = Settings()


# Export
__all__ = [
    'Settings',
    'settings',
    'LLMConfig',
    'RAGConfig',
    'TTSConfig',
    'AgentConfig',
    'ToolsConfig',
    'ConnectorsConfig',
    'AuthConfig',
    'LoggingConfig',
]
