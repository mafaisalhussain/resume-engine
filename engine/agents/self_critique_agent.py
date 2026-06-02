from __future__ import annotations

from typing import Any

from engine.agents.base_agent import BaseAgent
from engine.config import MAX_TOKENS, MODEL_CLAUDE
from engine.models import ATSScore, RecruiterScore, SelfCritiqueReport


class SelfCritiqueAgent(BaseAgent):
    def run(self, context: dict[str, Any]) -> SelfCritiqueReport:
        latex: str = context["latex"]
        jd_text: str = context["jd_text"]
        ats: ATSScore = context["ats_score"]
        rec: RecruiterScore = context["rec_score"]

        user_message = self._build_user_message(latex, jd_text, ats, rec)

        if self._verbose:
            print("\n[self_critique] Running adversarial review (Claude)...")

        raw = self._call_json(
            agent_name="self_critique",
            user_message=user_message,
            model=MODEL_CLAUDE,
            max_tokens=MAX_TOKENS["self_critique"],
        )

        return SelfCritiqueReport(
            honest_weaknesses=raw.get("honest_weaknesses", []),
            interview_risks=raw.get("interview_risks", []),
            strongest_elements=raw.get("strongest_elements", []),
            final_recommendation=raw.get("final_recommendation", "REVISE"),
            confidence_score=raw.get("confidence_score", 50),
        )

    @staticmethod
    def _build_user_message(
        latex: str,
        jd_text: str,
        ats: ATSScore,
        rec: RecruiterScore,
    ) -> str:
        fail_count = sum(1 for v in ats.violations if v.severity == "FAIL")
        warn_count = sum(1 for v in ats.violations if v.severity == "WARN")
        ats_summary = (
            f"Score: {ats.score}/80 ({'PASS' if ats.passes else 'FAIL'})\n"
            f"Violations: {fail_count} FAIL, {warn_count} WARN\n"
            f"Keyword misses: {', '.join(ats.keyword_misses) if ats.keyword_misses else 'none'}\n"
            f"Fabrication flags: {', '.join(ats.fabrication_flags) if ats.fabrication_flags else 'none'}"
        )
        rec_summary = (
            f"Score: {rec.total_score}/80 ({'PASS' if rec.passes else 'FAIL'})\n"
            f"Top weaknesses: {'; '.join(rec.top_weaknesses) if rec.top_weaknesses else 'none'}"
        )
        return (
            "═══════════════════════════════════════════\n"
            "JOB DESCRIPTION\n"
            "═══════════════════════════════════════════\n"
            f"{jd_text}\n\n"
            "═══════════════════════════════════════════\n"
            "ATS REVIEW FINDINGS\n"
            "═══════════════════════════════════════════\n"
            f"{ats_summary}\n\n"
            "═══════════════════════════════════════════\n"
            "RECRUITER REVIEW FINDINGS\n"
            "═══════════════════════════════════════════\n"
            f"{rec_summary}\n\n"
            "═══════════════════════════════════════════\n"
            "RESUME (LaTeX source)\n"
            "═══════════════════════════════════════════\n"
            f"{latex}"
        )
