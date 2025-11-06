"""
FARADAY AI - LLM Engine
Multi-provider LLM support (OpenAI, Anthropic, Local models)
"""

import asyncio
from typing import Optional, List, Dict, Any, AsyncIterator, Callable
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import json

from config.settings import settings
from utils.logger import logger


class LLMEngine:
    """
    Multi-provider LLM Engine with streaming and function calling support.
    """

    def __init__(self):
        """Initialize LLM Engine with configured provider"""
        self.provider = settings.llm.primary_provider
        self.config = settings.llm

        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None

        if self.provider == "openai" or self.config.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.config.openai_api_key)
            logger.info("✅ OpenAI client initialized")

        if self.provider == "anthropic" or self.config.anthropic_api_key:
            self.anthropic_client = AsyncAnthropic(api_key=self.config.anthropic_api_key)
            logger.info("✅ Anthropic client initialized")

        logger.info(f"🤖 LLM Engine initialized with provider: {self.provider}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate text from LLM with streaming support.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature override (optional)
            max_tokens: Max tokens override (optional)
            stream: Enable streaming (default: True)
            **kwargs: Additional provider-specific parameters

        Yields:
            Generated text chunks
        """
        try:
            temperature = temperature or self.config.temperature
            max_tokens = max_tokens or self.config.max_tokens

            if self.provider == "openai":
                async for chunk in self._generate_openai(prompt, system_prompt, temperature, max_tokens, stream, **kwargs):
                    yield chunk

            elif self.provider == "anthropic":
                async for chunk in self._generate_anthropic(prompt, system_prompt, temperature, max_tokens, stream, **kwargs):
                    yield chunk

            elif self.provider == "local":
                async for chunk in self._generate_local(prompt, system_prompt, temperature, max_tokens, stream, **kwargs):
                    yield chunk

            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            logger.error(f"❌ Error generating text: {e}")
            yield f"Error: {str(e)}"

    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate text using OpenAI API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.openai_client.chat.completions.create(
            model=self.config.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
        )

        if stream:
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            yield response.choices[0].message.content

    async def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate text using Anthropic API"""
        params = {
            "model": self.config.anthropic_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }

        if system_prompt:
            params["system"] = system_prompt

        if stream:
            async with self.anthropic_client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            response = await self.anthropic_client.messages.create(**params)
            yield response.content[0].text

    async def _generate_local(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate text using local model (placeholder for Unsloth/GGUF models)"""
        # This is a placeholder - implement with transformers or llama.cpp
        logger.warning("⚠️  Local model inference not yet implemented")
        yield "Local model inference is not yet implemented. Please use OpenAI or Anthropic provider."

    async def generate_with_functions(
        self,
        prompt: str,
        functions: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        max_iterations: int = 5,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate text with function calling support.
        Automatically executes functions and continues conversation.

        Args:
            prompt: User prompt
            functions: List of function definitions
            system_prompt: System prompt
            max_iterations: Max function calling iterations
            callback: Optional callback for streaming updates

        Returns:
            Final response dict with content and function calls
        """
        try:
            if self.provider != "openai":
                logger.warning("⚠️  Function calling only supported with OpenAI provider")
                result = ""
                async for chunk in self.generate(prompt, system_prompt):
                    result += chunk
                return {"content": result, "function_calls": []}

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            function_calls = []
            iterations = 0

            while iterations < max_iterations:
                response = await self.openai_client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=messages,
                    functions=functions,
                    function_call="auto",
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )

                message = response.choices[0].message

                # Check if function calling is needed
                if message.function_call:
                    function_name = message.function_call.name
                    function_args = json.loads(message.function_call.arguments)

                    logger.info(f"🔧 Function call: {function_name}({function_args})")

                    # Store function call
                    function_calls.append({
                        "name": function_name,
                        "arguments": function_args,
                    })

                    # Execute function (this should be handled by the tool registry)
                    # For now, we'll just add the function call to messages
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": function_name,
                            "arguments": json.dumps(function_args)
                        }
                    })

                    # Add placeholder result (actual execution should happen externally)
                    messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps({"status": "success", "note": "Function executed"})
                    })

                    iterations += 1

                    if callback:
                        await callback({
                            "type": "function_call",
                            "function": function_name,
                            "arguments": function_args
                        })

                else:
                    # No more function calls, return final response
                    return {
                        "content": message.content,
                        "function_calls": function_calls
                    }

            # Max iterations reached
            logger.warning(f"⚠️  Max function calling iterations ({max_iterations}) reached")
            return {
                "content": "Maximum function calling iterations reached.",
                "function_calls": function_calls
            }

        except Exception as e:
            logger.error(f"❌ Error in function calling: {e}")
            return {
                "content": f"Error: {str(e)}",
                "function_calls": function_calls if 'function_calls' in locals() else []
            }

    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (approximate).

        Args:
            text: Input text

        Returns:
            Approximate token count
        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4

    def get_model_name(self) -> str:
        """Get current model name"""
        if self.provider == "openai":
            return self.config.openai_model
        elif self.provider == "anthropic":
            return self.config.anthropic_model
        elif self.provider == "local":
            return self.config.local_model
        return "unknown"

    def get_provider(self) -> str:
        """Get current provider"""
        return self.provider


# Singleton instance
_llm_engine_instance = None


def get_llm_engine() -> LLMEngine:
    """Get or create LLM Engine singleton"""
    global _llm_engine_instance
    if _llm_engine_instance is None:
        _llm_engine_instance = LLMEngine()
    return _llm_engine_instance


# Export
__all__ = ['LLMEngine', 'get_llm_engine']
