from __future__ import annotations

import json
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from openai import OpenAI, RateLimitError, APIError

from engine.config import PROMPTS_DIR


class BaseAgent(ABC):
    def __init__(
        self,
        client: OpenAI,
        kb_cache_content: str,
        *,
        verbose: bool = False,
    ) -> None:
        self._client = client
        self._kb_cache_content = kb_cache_content
        self._verbose = verbose

    @abstractmethod
    def run(self, context: dict[str, Any]) -> Any:
        ...

    # ── Ollama call with retry ─────────────────────────────────────────────

    def _call(
        self,
        *,
        agent_name: str,
        user_message: str,
        model: str,
        max_tokens: int,
    ) -> str:
        print(f"[STEP_START] {self.__class__.__name__}", flush=True)
        agent_prompt = self._load_prompt(agent_name)

        # Agent instructions go FIRST so they are never truncated, then KB content
        system_content = agent_prompt
        if self._kb_cache_content:
            system_content += "\n\n---\n\n" + self._kb_cache_content

        from engine.config import MODEL_CLAUDE
        if model == MODEL_CLAUDE:
            return self._call_claude_subprocess(
                agent_name=agent_name,
                system_content=system_content,
                user_message=user_message,
            )

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ]

        delays = [5, 15, 45]
        last_error: Exception | None = None

        for attempt, delay in enumerate(delays, 1):
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    extra_body={"think": False},  # disable Qwen3 thinking blocks via Ollama API
                )
                text = response.choices[0].message.content or ""

                # Strip Qwen3 thinking blocks if they leaked through
                text = self._strip_thinking(text)

                if self._verbose:
                    usage = response.usage
                    if usage:
                        print(
                            f"  [{agent_name}] tokens in={usage.prompt_tokens} "
                            f"out={usage.completion_tokens}"
                        )

                return text

            except RateLimitError as exc:
                last_error = exc
                if attempt < len(delays):
                    if self._verbose:
                        print(f"  [{agent_name}] rate limit, retrying in {delay}s...")
                    time.sleep(delay)
            except APIError as exc:
                raise RuntimeError(f"[{agent_name}] API error: {exc}") from exc

        raise RuntimeError(
            f"[{agent_name}] rate limit after {len(delays)} attempts"
        ) from last_error

    # ── Claude CLI subprocess call ─────────────────────────────────────────

    def _call_claude_subprocess(
        self,
        *,
        agent_name: str,
        system_content: str,
        user_message: str,
    ) -> str:
        # Combine into one stdin payload — Claude handles XML role delimiters well
        full_prompt = (
            "<system_instructions>\n"
            + system_content
            + "\n</system_instructions>\n\n"
            + user_message
        )

        result = subprocess.run(
            "claude -p",
            input=full_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=True,
            timeout=300,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"[{agent_name}] claude subprocess failed (exit {result.returncode}): "
                f"{result.stderr[:500]}"
            )

        if self._verbose:
            print(f"  [{agent_name}] claude: {len(result.stdout)} chars returned")
        return result.stdout.strip()

    # ── JSON call with one retry on parse failure ──────────────────────────

    def _call_json(
        self,
        *,
        agent_name: str,
        user_message: str,
        model: str,
        max_tokens: int,
    ) -> dict[str, Any]:
        raw = self._call(
            agent_name=agent_name,
            user_message=user_message,
            model=model,
            max_tokens=max_tokens,
        )

        try:
            return self._parse_json(raw)
        except (json.JSONDecodeError, ValueError):
            if self._verbose:
                print(f"  [{agent_name}] JSON parse failed, retrying with correction prompt...")

            correction_msg = (
                user_message
                + "\n\n---\nYour previous response was not valid JSON. "
                "Return ONLY the JSON object — no explanation, no code fences, no commentary."
            )
            raw2 = self._call(
                agent_name=agent_name,
                user_message=correction_msg,
                model=model,
                max_tokens=max_tokens,
            )
            try:
                return self._parse_json(raw2)
            except (json.JSONDecodeError, ValueError) as exc:
                raise RuntimeError(
                    f"[{agent_name}] JSON parse failed after retry.\nRaw output:\n{raw2}"
                ) from exc

    @staticmethod
    def _strip_thinking(text: str) -> str:
        """Remove Qwen3 <think>...</think> blocks and trailing EOS fragments."""
        import re as _re
        # Remove explicit thinking blocks
        text = _re.sub(r"<think>.*?</think>", "", text, flags=_re.DOTALL)
        # Remove anything after </s> EOS token that Ollama sometimes emits
        if "</s>" in text:
            text = text[: text.index("</s>")]
        return text.strip()

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[-1].strip() == "```":
                lines = lines[1:-1]
            text = "\n".join(lines)
        return json.loads(text)

    @staticmethod
    def _load_prompt(agent_name: str) -> str:
        path: Path = PROMPTS_DIR / f"{agent_name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
