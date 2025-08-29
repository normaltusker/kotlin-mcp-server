#!/usr/bin/env python3
"""
General LLM access tool.

This module exposes a lightweight interface for querying language models from
within the MCP server. It supports local and external providers, optional
streaming responses and a privacy mode that prevents data from leaving the
machine. Responses include simple token usage accounting so callers can track
approximate costs.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ai.llm_integration import LLMProvider
from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


@dataclass
class LLMChunk:
    """A single streamed chunk from the LLM."""

    content: str


class LLMTool(IntelligentToolBase):
    """Tool that provides generic access to large language models."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the LLM query with optional streaming and privacy controls."""

        prompt: str = arguments.get("prompt", "")
        provider_name: str = arguments.get("provider", LLMProvider.LOCAL.value)
        stream: bool = bool(arguments.get("stream", False))
        privacy_mode: bool = bool(arguments.get("privacy_mode", False))

        if not prompt:
            return {"success": False, "error": "No prompt supplied"}

        provider = (
            LLMProvider(provider_name)
            if provider_name in LLMProvider._value2member_map_
            else LLMProvider.LOCAL
        )

        # Prevent external requests when privacy mode is enabled
        if privacy_mode and provider not in (LLMProvider.LOCAL, LLMProvider.CALLING_LLM):
            return {
                "success": False,
                "error": "External providers disabled in privacy mode",
                "provider": provider.value,
            }

        if stream:
            chunks, final_response = await self._stream_response(provider, prompt)
        else:
            final_response = await self._single_response(provider, prompt)
            chunks = None

        usage = self._estimate_usage(prompt, final_response)

        result: Dict[str, Any] = {
            "success": True,
            "provider": provider.value,
            "response": final_response,
            "usage": usage,
        }
        if chunks is not None:
            result["stream"] = [c.content for c in chunks]
        return result

    async def _single_response(self, provider: LLMProvider, prompt: str) -> str:
        """Get a complete response from the specified provider."""
        if provider == LLMProvider.LOCAL:
            # Trivial local implementation - reverse the prompt
            await asyncio.sleep(0)
            return prompt[::-1]
        return await self._call_external_provider(provider, prompt)

    async def _stream_response(
        self, provider: LLMProvider, prompt: str
    ) -> Tuple[List[LLMChunk], str]:
        """Stream a response token-by-token."""
        if provider == LLMProvider.LOCAL:
            chunks: List[LLMChunk] = []
            reversed_words = [w[::-1] for w in prompt.split()]
            for word in reversed_words:
                await asyncio.sleep(0)
                chunks.append(LLMChunk(content=word + " "))
            final = "".join(c.content for c in chunks).strip()
            return chunks, final
        return await self._stream_external_provider(provider, prompt)

    async def _call_external_provider(self, provider: LLMProvider, prompt: str) -> str:
        """Call an external provider such as OpenAI. Fallback to echo on failure."""
        try:
            import openai  # type: ignore

            if provider == LLMProvider.OPENAI:
                client = openai.AsyncOpenAI()
                resp = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.choices[0].message.content or ""  # type: ignore[attr-defined]
        except Exception:
            pass

        # Fallback behaviour
        await asyncio.sleep(0)
        return f"[{provider.value}] {prompt}"

    async def _stream_external_provider(
        self, provider: LLMProvider, prompt: str
    ) -> Tuple[List[LLMChunk], str]:
        """Stream from external provider; fallback to single response on failure."""
        try:
            import openai  # type: ignore

            if provider == LLMProvider.OPENAI:
                client = openai.AsyncOpenAI()
                stream = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                )
                chunks: List[LLMChunk] = []
                async for part in stream:
                    delta = part.choices[0].delta.content or ""  # type: ignore[attr-defined]
                    if delta:
                        chunks.append(LLMChunk(content=delta))
                final = "".join(c.content for c in chunks)
                return chunks, final
        except Exception:
            pass

        text = await self._call_external_provider(provider, prompt)
        return [LLMChunk(content=text)], text

    def _estimate_usage(self, prompt: str, completion: str) -> Dict[str, int]:
        """Approximate token usage using whitespace tokenisation."""
        prompt_tokens = len(prompt.split())
        completion_tokens = len(completion.split())
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }
