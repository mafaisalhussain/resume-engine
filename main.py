"""Resume Engine — CLI entry point.

Usage:
    python main.py generate --jd jd/loomai.md --company "loomAI" [--verbose]
    python main.py optimize --resume outputs/loomai/loomai_resume.md --jd jd/loomai.md [--verbose]

Requires Ollama running locally: https://ollama.com
    ollama pull mistral
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _slugify(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def _build_client():
    """Return an OpenAI-compatible client pointed at the local Ollama server."""
    from openai import OpenAI
    from engine.config import OLLAMA_BASE_URL
    # Ollama requires api_key to be set but ignores the value
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")


def cmd_generate(args: argparse.Namespace) -> None:
    from engine.agents.resume_writer_agent import ResumeWriterAgent, run_latex_pre_check
    from engine.knowledge_loader import KnowledgeLoader
    from engine.output_writer import OutputWriter

    jd_path = Path(args.jd)
    if not jd_path.exists():
        print(f"ERROR: JD file not found: {jd_path}")
        sys.exit(1)

    company_slug = _slugify(args.company)
    jd_text = jd_path.read_text(encoding="utf-8")

    print("Resume Engine — Generate")
    print(f"  Company   : {args.company} ({company_slug})")
    print(f"  JD        : {jd_path}")
    print()

    print("[STEP_START] KnowledgeLoader", flush=True)
    print("Loading knowledge base...")
    loader = KnowledgeLoader()
    kb = loader.load_all()
    cache_content = loader.build_cache_content(kb)
    print(f"  KB loaded: {len(kb.projects)} projects, {len(cache_content):,} chars")

    client = _build_client()

    writer = ResumeWriterAgent(client, cache_content, verbose=args.verbose)
    latex = writer.run({
        "jd_text": jd_text,
        "company_name": args.company,
        "revision_context": "",
        "iteration": 1,
    })

    violations = run_latex_pre_check(latex)
    if violations:
        print("\nWARNING: LaTeX pre-check violations detected:")
        for v in violations:
            print(f"  - {v}")
    else:
        print("  Pre-check: CLEAN")

    out = OutputWriter()
    resume_path = out.write_resume(company_slug, latex)
    print(f"\nResume saved: {resume_path}")
    print("Done.")


def cmd_optimize(args: argparse.Namespace) -> None:
    from engine.pipelines.optimize_pipeline import run_optimize_pipeline

    resume_path = Path(args.resume)
    jd_path = Path(args.jd)

    if not resume_path.exists():
        print(f"ERROR: Resume file not found: {resume_path}")
        sys.exit(1)
    if not jd_path.exists():
        print(f"ERROR: JD file not found: {jd_path}")
        sys.exit(1)

    print("Resume Engine — Optimize")
    print(f"  Resume    : {resume_path}")
    print(f"  JD        : {jd_path}")
    print()

    result = run_optimize_pipeline(resume_path, jd_path, verbose=args.verbose)

    ats = result.revised_ats_score
    rec = result.revised_recruiter_score
    learning = result.learning_update

    print(f"\nATS Score      : {ats.score}/80 ({'PASS' if ats.passes else 'FAIL'})")
    print(f"Recruiter Score: {rec.total_score}/80 ({'PASS' if rec.passes else 'FAIL'})")
    print(f"Combined       : {ats.score + rec.total_score}/160")

    if ats.keyword_misses:
        print(f"Keyword misses : {', '.join(ats.keyword_misses)}")

    lessons_total = (
        len(learning.ats_lessons_appended)
        + len(learning.recruiter_lessons_appended)
        + len(learning.successful_patterns_appended)
        + len(learning.weak_patterns_appended)
    )
    print(f"\nLearning       : {lessons_total} lessons appended to knowledge/learning/")
    if learning.summary:
        print(f"Summary        : {learning.summary}")
    print("\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="resume-engine",
        description="Self-improving AI resume generation engine (powered by Ollama)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen = subparsers.add_parser("generate", help="Generate a tailored resume")
    gen.add_argument("--jd", required=True, help="Path to job description .md file")
    gen.add_argument("--company", required=True, help="Company name (used for output directory)")
    gen.add_argument("--verbose", "-v", action="store_true", help="Print token usage per agent")

    opt = subparsers.add_parser("optimize", help="Update learning memory from an existing resume")
    opt.add_argument("--resume", required=True, help="Path to existing <company>_resume.md")
    opt.add_argument("--jd", required=True, help="Path to job description .md file")
    opt.add_argument("--verbose", "-v", action="store_true", help="Print token usage per agent")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "optimize":
        cmd_optimize(args)


if __name__ == "__main__":
    main()
