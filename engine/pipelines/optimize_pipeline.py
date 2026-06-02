from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from engine.agents.ats_review_agent import ATSReviewAgent
from engine.agents.learning_agent import LearningAgent
from engine.agents.recruiter_review_agent import RecruiterReviewAgent
from engine.agents.self_critique_agent import SelfCritiqueAgent
from engine.config import OLLAMA_BASE_URL
from engine.knowledge_loader import KnowledgeLoader
from engine.models import OptimizationResult
from engine.output_writer import OutputWriter


def run_optimize_pipeline(
    resume_path: str | Path,
    jd_path: str | Path,
    *,
    verbose: bool = False,
) -> OptimizationResult:
    latex = Path(resume_path).read_text(encoding="utf-8")
    jd_text = Path(jd_path).read_text(encoding="utf-8")

    print("[STEP_START] KnowledgeLoader", flush=True)
    print("Loading knowledge base...")
    loader = KnowledgeLoader()
    kb = loader.load_all()
    cache_content = loader.build_cache_content(kb)

    if verbose:
        print(f"  KB loaded: {len(kb.projects)} projects, {len(cache_content):,} chars")

    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    shared = dict(verbose=verbose)

    ats_score = ATSReviewAgent(client, cache_content, **shared).run(
        {"latex": latex, "jd_text": jd_text}
    )

    rec_score = RecruiterReviewAgent(client, cache_content, **shared).run(
        {"latex": latex, "jd_text": jd_text}
    )

    critique = SelfCritiqueAgent(client, cache_content, **shared).run(
        {"latex": latex, "jd_text": jd_text, "ats_score": ats_score, "rec_score": rec_score}
    )

    learning = LearningAgent(client, cache_content, **shared).run(
        {
            "latex": latex,
            "jd_text": jd_text,
            "ats_score": ats_score,
            "rec_score": rec_score,
            "critique": critique,
        }
    )

    writer = OutputWriter()

    def _fmt(lessons: list[str]) -> str:
        return "\n".join(f"- {lesson}" for lesson in lessons)

    if learning.ats_lessons_appended:
        writer.append_to_learning_file("ats_lessons", _fmt(learning.ats_lessons_appended))
    if learning.recruiter_lessons_appended:
        writer.append_to_learning_file("recruiter_lessons", _fmt(learning.recruiter_lessons_appended))
    if learning.successful_patterns_appended:
        writer.append_to_learning_file("successful_patterns", _fmt(learning.successful_patterns_appended))
    if learning.weak_patterns_appended:
        writer.append_to_learning_file("weak_patterns", _fmt(learning.weak_patterns_appended))

    return OptimizationResult(
        learning_update=learning,
        revised_ats_score=ats_score,
        revised_recruiter_score=rec_score,
        recommendations=rec_score.top_weaknesses + critique.honest_weaknesses,
    )
