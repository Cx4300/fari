#!/bin/bash

# FARADAY AI - Installation Script
# Prvi hrvatski LLM chat sustav 🇭🇷

set -e  # Exit on error

echo "============================================================"
echo "🇭🇷 FARADAY AI - Installation Script"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo "Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python version $PYTHON_VERSION is too old!${NC}"
    echo "Please install Python 3.9 or higher."
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists. Skipping.${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✅ Pip upgraded${NC}"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
echo "This may take several minutes..."
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/documents
mkdir -p data/faiss_index
mkdir -p data/artifacts
mkdir -p logs
mkdir -p credentials
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file and add your API keys!${NC}"
else
    echo -e "${YELLOW}ℹ️  .env file already exists. Skipping.${NC}"
fi
echo ""

# Optional: Download TTS models
echo "🎙️  TTS Model Setup"
echo "TTS models will be downloaded automatically on first use."
echo "To pre-download models, run: python -c 'from TTS.api import TTS; TTS(\"tts_models/hr/cv/vits\")'"
echo ""

# Optional: Unsloth installation
read -p "❓ Do you want to install Unsloth for local models? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing Unsloth..."
    pip install "unsloth @ git+https://github.com/unslothai/unsloth.git"
    echo -e "${GREEN}✅ Unsloth installed${NC}"
else
    echo -e "${YELLOW}⏭️  Skipping Unsloth installation${NC}"
fi
echo ""

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import chainlit
import langchain
import openai
import anthropic
from sentence_transformers import SentenceTransformer
print('✅ All core packages imported successfully!')
"
echo -e "${GREEN}✅ Installation test passed${NC}"
echo ""

# Print summary
echo "============================================================"
echo "🎉 Installation Complete!"
echo "============================================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Edit .env file with your API keys:"
echo "   ${BLUE}nano .env${NC}"
echo ""
echo "2. Add documents to data/documents/ for RAG (optional)"
echo ""
echo "3. Activate virtual environment:"
echo "   ${BLUE}source venv/bin/activate${NC}"
echo ""
echo "4. Run FARADAY AI:"
echo "   ${BLUE}chainlit run app.py${NC}"
echo ""
echo "5. Open browser at: ${BLUE}http://localhost:8000${NC}"
echo ""
echo "============================================================"
echo "🇭🇷 Dobrodošli u FARADAY AI!"
echo "============================================================"
