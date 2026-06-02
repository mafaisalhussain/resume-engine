from __future__ import annotations

from typing import Any

from engine.agents.base_agent import BaseAgent
from engine.config import MAX_TOKENS, MODEL_CLAUDE
from engine.models import RecruiterDimension, RecruiterScore


class RecruiterReviewAgent(BaseAgent):
    def run(self, context: dict[str, Any]) -> RecruiterScore:
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
            print("\n[recruiter_review] Scoring recruiter appeal...")

        raw = self._call_json(
            agent_name="recruiter_review",
            user_message=user_message,
            model=MODEL_CLAUDE,
            max_tokens=MAX_TOKENS["recruiter_review"],
        )

        dimensions = [RecruiterDimension(**d) for d in raw.get("dimensions", [])]
        return RecruiterScore(
            dimensions=dimensions,
            total_score=raw["total_score"],
            overall_assessment=raw.get("overall_assessment", ""),
            top_strengths=raw.get("top_strengths", []),
            top_weaknesses=raw.get("top_weaknesses", []),
            passes=raw["passes"],
            revision_instructions=raw.get("revision_instructions", ""),
        )
