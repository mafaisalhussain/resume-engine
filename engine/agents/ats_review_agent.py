from __future__ import annotations

from typing import Any

from engine.agents.base_agent import BaseAgent
from engine.config import MAX_TOKENS, MODEL_CLAUDE
from engine.models import ATSScore, ATSViolation


class ATSReviewAgent(BaseAgent):
    def run(self, context: dict[str, Any]) -> ATSScore:
        latex: str = context["latex"]
        jd_text: str = context["jd_text"]

        user_message = (
            "═══════════════════════════════════════════\n"
            "JOB DESCRIPTION\n"
            "═══════════════════════════════════════════\n"
            f"{jd_text}\n\n"
            "═══════════════════════════════════════════\n"
            "RESUME (LaTeX source)\n"
            "═══════════════════════════════════════════\n"
            f"{latex}"
        )

        if self._verbose:
            print("\n[ats_review] Scoring ATS compliance...")

        raw = self._call_json(
            agent_name="ats_review",
            user_message=user_message,
            model=MODEL_CLAUDE,
            max_tokens=MAX_TOKENS["ats_review"],
        )

        violations = [ATSViolation(**v) for v in raw.get("violations", [])]
        return ATSScore(
            score=raw["score"],
            violations=violations,
            keyword_hits=raw.get("keyword_hits", []),
            keyword_misses=raw.get("keyword_misses", []),
            fabrication_flags=raw.get("fabrication_flags", []),
            passes=raw["passes"],
            revision_instructions=raw.get("revision_instructions", ""),
        )
