from __future__ import annotations

import re
from typing import Any

from engine.agents.base_agent import BaseAgent
from engine.config import MAX_TOKENS, MODEL_CLAUDE


_PRECHECK_RULES: list[tuple[str, int, str]] = [
    # (pattern, re_flags, description)
    (r"\\documentclass", 0, "missing \\documentclass"),
    (r"\\end\{document\}", 0, "missing \\end{document}"),
]

_BANNED_PATTERNS: list[tuple[str, re.RegexFlag | int, str]] = [
    (r"```", 0, "code fence markers"),
    (r"LangChain", re.IGNORECASE, "LangChain"),
    (r"\$\\sim\$", 0, "$\\sim$ math tilde"),
    (r"Forage", re.IGNORECASE, "Forage certification"),
]


def run_latex_pre_check(latex: str) -> list[str]:
    """Return list of violation descriptions. Empty list means clean."""
    violations: list[str] = []

    for pattern, flags, desc in _PRECHECK_RULES:
        if not re.search(pattern, latex, flags):
            violations.append(f"MISSING: {desc}")

    for pattern, flags, desc in _BANNED_PATTERNS:
        if re.search(pattern, latex, flags):
            violations.append(f"BANNED content found: {desc}")

    return violations


class ResumeWriterAgent(BaseAgent):
    def __init__(
        self,
        client,
        kb_cache_content: str,
        *,
        verbose: bool = False,
    ) -> None:
        super().__init__(client, kb_cache_content, verbose=verbose)

    def run(self, context: dict[str, Any]) -> str:
        """Generate LaTeX resume. Returns raw LaTeX string."""
        jd_text: str = context["jd_text"]
        company_name: str = context["company_name"]
        revision_context: str = context.get("revision_context", "")
        iteration: int = context.get("iteration", 1)

        user_message = self._build_user_message(
            jd_text=jd_text,
            company_name=company_name,
            revision_context=revision_context,
            iteration=iteration,
        )

        if self._verbose:
            print(f"\n[resume_writer] Generating resume for {company_name} (iteration {iteration})...")

        raw = self._call(
            agent_name="resume_writer",
            user_message=user_message,
            model=MODEL_CLAUDE,
            max_tokens=MAX_TOKENS["resume_writer"],
        )

        return self._clamp_latex(raw)

    @staticmethod
    def _clamp_latex(text: str) -> str:
        """Strip everything before \\documentclass and after \\end{document}."""
        start_marker = r"\documentclass"
        end_marker = r"\end{document}"

        start = text.find(start_marker)
        if start == -1:
            return text.strip()
        text = text[start:]

        end = text.rfind(end_marker)
        if end != -1:
            text = text[: end + len(end_marker)]

        return text.strip()

    @staticmethod
    def _build_user_message(
        *,
        jd_text: str,
        company_name: str,
        revision_context: str,
        iteration: int,
    ) -> str:
        parts = [
            f"TARGET COMPANY: {company_name}",
            f"ITERATION: {iteration}",
            "",
            "═══════════════════════════════════════════",
            "JOB DESCRIPTION",
            "═══════════════════════════════════════════",
            jd_text,
        ]

        if revision_context:
            parts += [
                "",
                "═══════════════════════════════════════════",
                "REQUIRED FIXES FROM PRIOR ITERATION — YOU MUST ADDRESS EVERY ITEM BELOW",
                "═══════════════════════════════════════════",
                revision_context,
            ]

        parts += [
            "",
            "═══════════════════════════════════════════",
            "INSTRUCTIONS",
            "═══════════════════════════════════════════",
            "Write the complete tailored LaTeX resume for the job description above.",
            "Use the CANDIDATE PROFILE, PROJECTS, ANCHORED METRICS, and FRAMEWORKS",
            "from the knowledge base loaded in your context.",
            "",
            "Selection priority:",
            "1. Projects most relevant to this JD's domain — 3 to 5 projects",
            "2. Experience bullets that echo JD must-have keywords",
            "3. Skills categories mirroring the JD's skill groupings",
            "",
            "Your response is ONLY the LaTeX document. Start with \\documentclass.",
        ]

        return "\n".join(parts)
