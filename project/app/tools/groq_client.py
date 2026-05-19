import os
import asyncio
from typing import Any
import httpx

GROQ_API_URL = "https://api.groq.com/openai/v1/responses"

class GroqClient:
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self._client = httpx.AsyncClient(timeout=30.0)

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("Missing GROQ_API_KEY")

        payload = {
            "model": self.model_name,
            "input": prompt,
            "temperature": 0.3,
            "max_output_tokens": 700,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        retry = 0
        while retry < 5:
            try:
                response = await self._client.post(GROQ_API_URL, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict):
                    if "output_text" in data and isinstance(data["output_text"], str):
                        return data["output_text"].strip()
                    if "output" in data and isinstance(data["output"], list):
                        text = "\n".join(
                            str(item.get("content", "")) for item in data["output"] if isinstance(item, dict)
                        )
                        if text.strip():
                            return text.strip()
                    if "results" in data and data["results"]:
                        return str(data["results"][0]).strip()
                return str(data).strip()
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                retry += 1
                delay = 5 + 5 * retry
                if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
                    if exc.response.status_code == 429:
                        retry_after = exc.response.headers.get("Retry-After")
                        if retry_after and retry_after.isdigit():
                            delay = int(retry_after)
                if retry >= 5:
                    raise RuntimeError(f"Groq request failed: {exc}")
                await asyncio.sleep(delay)

    async def close(self):
        await self._client.aclose()
