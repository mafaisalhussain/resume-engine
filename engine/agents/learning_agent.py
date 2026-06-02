from __future__ import annotations

from datetime import date
from typing import Any

from engine.agents.base_agent import BaseAgent
from engine.config import MAX_TOKENS, MODEL_CLAUDE
from engine.models import ATSScore, LearningUpdate, RecruiterScore, SelfCritiqueReport


class LearningAgent(BaseAgent):
    def run(self, context: dict[str, Any]) -> LearningUpdate:
        latex: str = context["latex"]
        jd_text: str = context["jd_text"]
        ats: ATSScore = context["ats_score"]
        rec: RecruiterScore = context["rec_score"]
        critique: SelfCritiqueReport = context["critique"]
        today = date.today().isoformat()

        user_message = self._build_user_message(latex, jd_text, ats, rec, critique, today)

        if self._verbose:
            print("\n[learning] Extracting lessons...")

        raw = self._call_json(
            agent_name="learning",
            user_message=user_message,
            model=MODEL_CLAUDE,
            max_tokens=MAX_TOKENS["learning"],
        )

        return LearningUpdate(
            ats_lessons_appended=raw.get("ats_lessons_appended", []),
            recruiter_lessons_appended=raw.get("recruiter_lessons_appended", []),
            successful_patterns_appended=raw.get("successful_patterns_appended", []),
            weak_patterns_appended=raw.get("weak_patterns_appended", []),
            summary=raw.get("summary", ""),
        )

    @staticmethod
    def _build_user_message(
        latex: str,
        jd_text: str,
        ats: ATSScore,
        rec: RecruiterScore,
        critique: SelfCritiqueReport,
        today: str,
    ) -> str:
        dim_lines = "\n".join(
            f"  {d.dimension_id} {d.dimension_name}: {d.score}/10 — {d.rationale}"
            for d in rec.dimensions
        )
        violation_lines = (
            "\n".join(f"  [{v.severity}] {v.rule_id}: {v.description}" for v in ats.violations)
            if ats.violations else "  none"
        )
        return (
            f"TODAY_DATE: {today}\n\n"
            "═══════════════════════════════════════════\n"
            "JOB DESCRIPTION\n"
            "═══════════════════════════════════════════\n"
            f"{jd_text}\n\n"
            "═══════════════════════════════════════════\n"
            "ATS REVIEW\n"
            "═══════════════════════════════════════════\n"
            f"Score: {ats.score}/80\n"
            f"Keyword hits: {', '.join(ats.keyword_hits) if ats.keyword_hits else 'none'}\n"
            f"Keyword misses: {', '.join(ats.keyword_misses) if ats.keyword_misses else 'none'}\n"
            f"Fabrication flags: {', '.join(ats.fabrication_flags) if ats.fabrication_flags else 'none'}\n"
            f"Violations:\n{violation_lines}\n\n"
            "═══════════════════════════════════════════\n"
            "RECRUITER REVIEW\n"
            "═══════════════════════════════════════════\n"
            f"Total: {rec.total_score}/80\n"
            f"Dimensions:\n{dim_lines}\n"
            f"Top strengths: {'; '.join(rec.top_strengths)}\n"
            f"Top weaknesses: {'; '.join(rec.top_weaknesses)}\n\n"
            "═══════════════════════════════════════════\n"
            "SELF-CRITIQUE\n"
            "═══════════════════════════════════════════\n"
            f"Recommendation: {critique.final_recommendation} (confidence {critique.confidence_score}/100)\n"
            f"Honest weaknesses: {'; '.join(critique.honest_weaknesses)}\n"
            f"Interview risks: {'; '.join(critique.interview_risks)}\n"
            f"Strongest elements: {'; '.join(critique.strongest_elements)}\n\n"
            "═══════════════════════════════════════════\n"
            "RESUME (LaTeX source)\n"
            "═══════════════════════════════════════════\n"
            f"{latex}"
        )
