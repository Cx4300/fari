"""
FARADAY AI - TTS Engine
Coqui TTS for Croatian and English speech synthesis
"""

import asyncio
from typing import Optional, AsyncIterator
from pathlib import Path
import tempfile
import io

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

from config.settings import settings
from utils.logger import logger


class TTSEngine:
    """
    Text-to-Speech Engine using Coqui TTS.
    Supports Croatian and English speech synthesis.
    """

    def __init__(self):
        """Initialize TTS Engine"""
        self.config = settings.tts
        self.tts_hr = None
        self.tts_en = None
        self.current_language = self.config.default_language

        if not TTS_AVAILABLE:
            logger.warning("⚠️  TTS library not installed. Install with: pip install TTS")
            return

        if self.config.enabled:
            logger.info("🎙️  Initializing TTS Engine...")
            self._initialize_models()
        else:
            logger.info("ℹ️  TTS disabled in settings")

    def _initialize_models(self):
        """Initialize TTS models"""
        try:
            # Initialize Croatian model
            logger.info(f"Loading Croatian TTS model: {self.config.tts_model_hr}")
            self.tts_hr = TTS(model_name=self.config.tts_model_hr)
            logger.info("✅ Croatian TTS model loaded")

        except Exception as e:
            logger.error(f"❌ Failed to load Croatian TTS model: {e}")
            logger.info("ℹ️  Trying fallback model...")
            try:
                # Fallback to a more common model
                self.tts_hr = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
                logger.info("✅ Fallback TTS model loaded")
            except Exception as e2:
                logger.error(f"❌ Failed to load fallback model: {e2}")

        try:
            # Initialize English model
            logger.info(f"Loading English TTS model: {self.config.tts_model_en}")
            self.tts_en = TTS(model_name=self.config.tts_model_en)
            logger.info("✅ English TTS model loaded")

        except Exception as e:
            logger.error(f"❌ Failed to load English TTS model: {e}")
            # English can use the same model as Croatian if multilingual
            if self.tts_hr:
                self.tts_en = self.tts_hr
                logger.info("ℹ️  Using Croatian model for English as fallback")

    def set_language(self, language: str):
        """
        Set the current language.

        Args:
            language: Language code ('hr' or 'en')
        """
        if language.lower() in ['hr', 'en']:
            self.current_language = language.lower()
            logger.info(f"🌐 TTS language set to: {language}")
        else:
            logger.warning(f"⚠️  Unsupported language: {language}. Using default.")

    def _get_current_tts(self) -> Optional[TTS]:
        """Get TTS model for current language"""
        if self.current_language == 'hr':
            return self.tts_hr
        else:
            return self.tts_en or self.tts_hr

    async def synthesize_speech(
        self,
        text: str,
        output_path: Optional[Path] = None,
        language: Optional[str] = None
    ) -> Optional[Path]:
        """
        Synthesize speech from text and save to file.

        Args:
            text: Text to synthesize
            output_path: Output file path (optional, generates temp file if None)
            language: Language override (optional)

        Returns:
            Path to audio file, or None if failed
        """
        if not self.config.enabled or not TTS_AVAILABLE:
            logger.warning("⚠️  TTS not available")
            return None

        try:
            # Set language if specified
            if language:
                old_lang = self.current_language
                self.set_language(language)

            tts = self._get_current_tts()
            if not tts:
                logger.error("❌ No TTS model available")
                return None

            # Generate output path if not provided
            if output_path is None:
                temp_dir = Path(tempfile.gettempdir())
                output_path = temp_dir / f"tts_{hash(text)}.wav"

            # Synthesize speech
            logger.info(f"🎙️  Synthesizing speech ({len(text)} chars)...")

            await asyncio.to_thread(
                tts.tts_to_file,
                text=text,
                file_path=str(output_path)
            )

            logger.info(f"✅ Speech synthesized: {output_path}")

            # Restore language if changed
            if language:
                self.set_language(old_lang)

            return output_path

        except Exception as e:
            logger.error(f"❌ Error synthesizing speech: {e}")
            return None

    async def stream_speech(
        self,
        text: str,
        language: Optional[str] = None,
        chunk_size: int = 1024
    ) -> AsyncIterator[bytes]:
        """
        Stream audio chunks (useful for real-time playback).

        Args:
            text: Text to synthesize
            language: Language override
            chunk_size: Size of audio chunks

        Yields:
            Audio data chunks
        """
        if not self.config.enabled or not TTS_AVAILABLE:
            logger.warning("⚠️  TTS not available")
            return

        try:
            # Generate audio file first
            audio_path = await self.synthesize_speech(text, language=language)

            if not audio_path or not audio_path.exists():
                logger.error("❌ Failed to generate audio file")
                return

            # Stream audio file in chunks
            with open(audio_path, 'rb') as audio_file:
                while True:
                    chunk = audio_file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

            # Clean up temp file
            if audio_path.parent == Path(tempfile.gettempdir()):
                audio_path.unlink()

        except Exception as e:
            logger.error(f"❌ Error streaming speech: {e}")

    async def synthesize_to_bytes(
        self,
        text: str,
        language: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Synthesize speech and return as bytes.

        Args:
            text: Text to synthesize
            language: Language override

        Returns:
            Audio data as bytes, or None if failed
        """
        try:
            audio_path = await self.synthesize_speech(text, language=language)

            if not audio_path or not audio_path.exists():
                return None

            # Read audio file
            with open(audio_path, 'rb') as f:
                audio_data = f.read()

            # Clean up temp file
            if audio_path.parent == Path(tempfile.gettempdir()):
                audio_path.unlink()

            return audio_data

        except Exception as e:
            logger.error(f"❌ Error synthesizing to bytes: {e}")
            return None

    def is_available(self) -> bool:
        """Check if TTS is available"""
        return TTS_AVAILABLE and self.config.enabled and (self.tts_hr is not None or self.tts_en is not None)

    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        languages = []
        if self.tts_hr:
            languages.append('hr')
        if self.tts_en:
            languages.append('en')
        return languages

    def get_stats(self) -> dict:
        """Get TTS engine statistics"""
        return {
            "enabled": self.config.enabled,
            "available": self.is_available(),
            "current_language": self.current_language,
            "supported_languages": self.get_supported_languages(),
            "model_hr": self.config.tts_model_hr,
            "model_en": self.config.tts_model_en,
        }


# Singleton instance
_tts_engine_instance = None


def get_tts_engine() -> TTSEngine:
    """Get or create TTS Engine singleton"""
    global _tts_engine_instance
    if _tts_engine_instance is None:
        _tts_engine_instance = TTSEngine()
    return _tts_engine_instance


# Export
__all__ = ['TTSEngine', 'get_tts_engine']
