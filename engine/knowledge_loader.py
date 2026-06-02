from __future__ import annotations

from pathlib import Path

from engine.config import (
    FRAMEWORKS_DIR,
    KNOWLEDGE_DIR,
    LEARNING_DIR,
    PROJECTS_DIR,
)
from engine.models import KnowledgeBase, LearningContext


class KnowledgeLoader:
    def load_all(self) -> KnowledgeBase:
        projects = {
            p.stem: self._read(p)
            for p in sorted(PROJECTS_DIR.glob("*.md"))
        }

        kb = KnowledgeBase(
            profile_md=self._read(KNOWLEDGE_DIR / "profile.md"),
            action_verbs_md=self._read(KNOWLEDGE_DIR / "action_verbs.md"),
            metrics_md=self._read(KNOWLEDGE_DIR / "metrics" / "metrics.md"),
            ats_compliance_md=self._read(FRAMEWORKS_DIR / "ats_compliance.md"),
            resume_structure_md=self._read(FRAMEWORKS_DIR / "resume_structure.md"),
            vocabulary_bridges_md=self._read(FRAMEWORKS_DIR / "vocabulary_bridges.md"),
            evidence_classification_md=self._read(FRAMEWORKS_DIR / "evidence_classification.md"),
            fluff_blacklist_md=self._read(FRAMEWORKS_DIR / "fluff_blacklist.md"),
            prohibited_items_md=self._read(FRAMEWORKS_DIR / "prohibited_items.md"),
            projects=projects,
            learning_context=self.load_learning_files(),
        )
        return kb

    def load_learning_files(self) -> LearningContext:
        def _safe(name: str) -> str:
            path = LEARNING_DIR / f"{name}.md"
            if not path.exists():
                return ""
            content = path.read_text(encoding="utf-8")
            # Only read above the archive divider if present
            if "--- ARCHIVE ---" in content:
                content = content.split("--- ARCHIVE ---")[0]
            return content.strip()

        return LearningContext(
            ats_lessons=_safe("ats_lessons"),
            recruiter_lessons=_safe("recruiter_lessons"),
            successful_patterns=_safe("successful_patterns"),
            weak_patterns=_safe("weak_patterns"),
        )

    def build_cache_content(self, kb: KnowledgeBase) -> str:
        """Concatenate all static KB files into one cacheable block."""
        sections = [
            ("CANDIDATE PROFILE", kb.profile_md),
            ("ACTION VERBS", kb.action_verbs_md),
            ("ANCHORED METRICS", kb.metrics_md),
            ("ATS COMPLIANCE RULES", kb.ats_compliance_md),
            ("RESUME SECTION ORDER", kb.resume_structure_md),
            ("VOCABULARY BRIDGES", kb.vocabulary_bridges_md),
            ("EVIDENCE CLASSIFICATION FRAMEWORK", kb.evidence_classification_md),
            ("FLUFF WORD BLACKLIST", kb.fluff_blacklist_md),
            ("PROHIBITED ITEMS", kb.prohibited_items_md),
        ]

        for stem, content in sorted(kb.projects.items()):
            sections.append((f"PROJECT: {stem.upper()}", content))

        parts = []
        for title, content in sections:
            parts.append(f"=== {title} ===\n\n{content}")

        return "\n\n" + "\n\n".join(parts) + "\n"

    @staticmethod
    def _read(path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8").strip()
