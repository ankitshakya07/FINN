"""Small/strong model router with schema validation, SHA-256 caching and cost logging.

Provider contract: OpenAI-compatible POST /chat/completions.
LLMs extract/classify/judge only. Financial arithmetic belongs in deterministic code.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ValidationError

from .db import connect

logger = logging.getLogger("finn.llm")
Tier = Literal["small", "strong"]


@dataclass(frozen=True)
class ModelConfig:
    name: str
    input_cost_per_1m: float
    output_cost_per_1m: float


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def model_config(tier: Tier) -> ModelConfig:
    if tier == "small":
        return ModelConfig(
            os.getenv("LLM_SMALL_MODEL", "gpt-4.1-mini"),
            _float_env("LLM_SMALL_INPUT_COST_PER_1M", 0.40),
            _float_env("LLM_SMALL_OUTPUT_COST_PER_1M", 1.60),
        )
    return ModelConfig(
        os.getenv("LLM_STRONG_MODEL", "gpt-4.1"),
        _float_env("LLM_STRONG_INPUT_COST_PER_1M", 2.00),
        _float_env("LLM_STRONG_OUTPUT_COST_PER_1M", 8.00),
    )


def canonical_hash(*parts: Any) -> str:
    payload = json.dumps(parts, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _schema_for(schema: type[BaseModel] | dict[str, Any]) -> dict[str, Any]:
    return schema.model_json_schema() if isinstance(schema, type) and issubclass(schema, BaseModel) else schema


def _cache_get(key: str, db_path: str | None = None) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT value FROM llm_cache WHERE key=?", (key,)).fetchone()
        if row:
            conn.execute("UPDATE llm_cache SET last_used_at=CURRENT_TIMESTAMP WHERE key=?", (key,))
            return json.loads(row["value"])
    return None


def _cache_put(key: str, value: dict[str, Any], model: str, input_tokens: int,
               output_tokens: int, cost: float, db_path: str | None = None) -> None:
    with connect(db_path) as conn:
        conn.execute(
            """INSERT OR REPLACE INTO llm_cache
               (key,value,model,tokens,input_tokens,output_tokens,cost,last_used_at)
               VALUES (?,?,?,?,?,?,?,CURRENT_TIMESTAMP)""",
            (key, json.dumps(value, ensure_ascii=False), model,
             input_tokens + output_tokens, input_tokens, output_tokens, cost),
        )


async def generate_json(
    *,
    system: str,
    user: str,
    schema: type[BaseModel] | dict[str, Any],
    tier: Tier = "small",
    temperature: float = 0.0,
    db_path: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Return schema-valid JSON. Successful responses are cached by exact content hash."""
    cfg = model_config(tier)
    json_schema = _schema_for(schema)
    cache_key = canonical_hash(cfg.name, system, user, json_schema, temperature)

    if not force_refresh:
        cached = _cache_get(cache_key, db_path)
        if cached is not None:
            logger.info("llm_cache_hit key=%s model=%s", cache_key, cfg.name)
            return cached

    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        raise RuntimeError("LLM_API_KEY is not configured")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
    retries = int(os.getenv("LLM_MAX_RETRIES", "2"))
    body = {
        "model": cfg.name,
        "temperature": temperature,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "finn_response", "strict": True, "schema": json_schema},
        },
    }

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json=body,
                )
                response.raise_for_status()
                payload = response.json()
            content = payload["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            if isinstance(schema, type) and issubclass(schema, BaseModel):
                parsed = schema.model_validate(parsed).model_dump(mode="json")
            usage = payload.get("usage", {})
            input_tokens = int(usage.get("prompt_tokens", 0))
            output_tokens = int(usage.get("completion_tokens", 0))
            cost = (input_tokens * cfg.input_cost_per_1m + output_tokens * cfg.output_cost_per_1m) / 1_000_000
            _cache_put(cache_key, parsed, cfg.name, input_tokens, output_tokens, cost, db_path)
            logger.info(
                "llm_usage tier=%s model=%s input_tokens=%d output_tokens=%d cost_usd=%.8f cache_key=%s",
                tier, cfg.name, input_tokens, output_tokens, cost, cache_key,
            )
            return parsed
        except (httpx.HTTPError, KeyError, ValueError, ValidationError) as exc:
            last_error = exc
            if attempt >= retries:
                break
            delay = min(2 ** attempt + random.random() * 0.25, 8)
            logger.warning("llm_retry attempt=%d error=%s sleep=%.2f", attempt + 1, exc, delay)
            import asyncio
            await asyncio.sleep(delay)

    raise RuntimeError(f"LLM request failed after {retries + 1} attempts: {last_error}") from last_error
