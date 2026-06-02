from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from engine.config import LEARNING_DIR, OUTPUTS_DIR
from engine.models import ResumeMetadata, ScoreReport


class OutputWriter:
    def write_resume(self, company_slug: str, latex_content: str) -> Path:
        out_dir = self._ensure_output_dir(company_slug)
        path = out_dir / f"{company_slug}_resume.md"
        path.write_text(latex_content, encoding="utf-8")
        return path

    def write_score_report(self, company_slug: str, report: ScoreReport) -> Path:
        out_dir = self._ensure_output_dir(company_slug)
        path = out_dir / f"{company_slug}_score_report.md"
        path.write_text(self._render_score_report(report), encoding="utf-8")
        return path

    def write_metadata(self, company_slug: str, metadata: ResumeMetadata) -> Path:
        out_dir = self._ensure_output_dir(company_slug)
        path = out_dir / f"{company_slug}_metadata.json"
        path.write_text(metadata.model_dump_json(indent=2), encoding="utf-8")
        return path

    def append_to_learning_file(self, filename: str, content: str) -> None:
        """Append content to a learning file, creating it if absent."""
        LEARNING_DIR.mkdir(parents=True, exist_ok=True)
        path = LEARNING_DIR / f"{filename}.md"
        with path.open("a", encoding="utf-8") as f:
            f.write("\n\n" + content)

    # ── Internal helpers ───────────────────────────────────────────────────

    @staticmethod
    def _ensure_output_dir(company_slug: str) -> Path:
        out_dir = OUTPUTS_DIR / company_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @staticmethod
    def _render_score_report(report: ScoreReport) -> str:
        ats = report.ats_score
        rec = report.recruiter_score
        crit = report.self_critique
        ts = report.generation_timestamp

        lines = [
            f"# Score Report — {ts}",
            "",
            f"**Combined Score:** {report.combined_score} / 160 (ATS max 80 + Recruiter max 80)",
            f"**Iterations used:** {report.iteration_count}",
            "",
            "---",
            "",
            "## ATS Score",
            f"**Score:** {ats.score} / 80 — {'PASS' if ats.passes else 'FAIL'}",
            "",
            "### Keyword Hits",
            ", ".join(ats.keyword_hits) if ats.keyword_hits else "_none_",
            "",
            "### Keyword Misses",
            ", ".join(ats.keyword_misses) if ats.keyword_misses else "_none_",
            "",
        ]

        if ats.violations:
            lines += ["### ATS Violations", ""]
            for v in ats.violations:
                lines.append(f"- **[{v.severity}]** `{v.rule_id}`: {v.description} *(at: {v.location})*")
            lines.append("")

        if ats.fabrication_flags:
            lines += ["### Fabrication Flags", ""]
            for f in ats.fabrication_flags:
                lines.append(f"- {f}")
            lines.append("")

        lines += [
            "### ATS Revision Instructions",
            ats.revision_instructions,
            "",
            "---",
            "",
            "## Recruiter Score",
            f"**Score:** {rec.total_score} / 80 — {'PASS' if rec.passes else 'FAIL'}",
            "",
            "### Dimension Scores",
            "",
        ]

        for dim in rec.dimensions:
            lines.append(f"- **{dim.dimension_id} {dim.dimension_name}:** {dim.score}/10 — {dim.rationale}")

        lines += [
            "",
            "### Top Strengths",
            *[f"- {s}" for s in rec.top_strengths],
            "",
            "### Top Weaknesses",
            *[f"- {w}" for w in rec.top_weaknesses],
            "",
            "### Recruiter Revision Instructions",
            rec.revision_instructions,
            "",
            "---",
            "",
            "## Self-Critique",
            f"**Recommendation:** {crit.final_recommendation} (confidence {crit.confidence_score}/100)",
            "",
            "### Honest Weaknesses",
            *[f"- {w}" for w in crit.honest_weaknesses],
            "",
            "### Interview Risks",
            *[f"- {r}" for r in crit.interview_risks],
            "",
            "### Strongest Elements",
            *[f"- {s}" for s in crit.strongest_elements],
        ]

        return "\n".join(lines)
