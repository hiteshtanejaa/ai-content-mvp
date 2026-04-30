import os
from dataclasses import dataclass

import openai
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMClient:
    """Bundled LLM configuration passed to agents."""
    client: openai.AsyncOpenAI
    model: str
    temperature: float


def get_llm(temperature: float = 0.7) -> LLMClient:
    """
    Model factory — returns a configured async OpenAI-compatible client.

    To swap providers, set only .env:
      OpenAI (default):  LLM_MODEL=gpt-4o
      Together.ai:       LLM_BASE_URL=https://api.together.xyz/v1
                         LLM_API_KEY=<together_key>
                         LLM_MODEL=meta-llama/Llama-3-70b-chat-hf
      Groq:              LLM_BASE_URL=https://api.groq.com/openai/v1
                         LLM_API_KEY=<groq_key>
                         LLM_MODEL=llama3-70b-8192
    """
    model = os.getenv("LLM_MODEL", "gpt-4o")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LLM_BASE_URL") or None  # None = OpenAI default endpoint

    client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)

    return LLMClient(client=client, model=model, temperature=temperature)
