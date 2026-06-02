from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
JD_DIR = ROOT_DIR / "jd"
OUTPUTS_DIR = ROOT_DIR / "outputs"
HISTORY_DIR = KNOWLEDGE_DIR / "history"
LEARNING_DIR = KNOWLEDGE_DIR / "learning"
PROMPTS_DIR = ROOT_DIR / "engine" / "prompts"
FRAMEWORKS_DIR = KNOWLEDGE_DIR / "frameworks"
PROJECTS_DIR = KNOWLEDGE_DIR / "projects"

# Ollama local inference — no API key required
OLLAMA_BASE_URL = "http://localhost:11434/v1"

# Custom model built on qwen3.5:9b with num_ctx=32768 and temperature=0.3
# Created via: ollama create resume-engine -f Modelfile
MODEL_STRONG = "resume-engine"
MODEL_FAST = "resume-engine"
MODEL_CLAUDE = "__claude__"  # sentinel — routes _call() to claude CLI subprocess

MAX_ITERATIONS = 5
SCORE_THRESHOLD = 80

MAX_TOKENS: dict[str, int] = {
    "knowledge_extraction": 4096,
    "job_analysis": 2048,
    "gap_coverage": 4096,
    "resume_strategy": 3000,
    "resume_writer": 8192,
    "ats_review": 4096,
    "recruiter_review": 4096,
    "self_critique": 4096,
    "learning": 4096,
}

LEARNING_FILES = {
    "ats_lessons": LEARNING_DIR / "ats_lessons.md",
    "recruiter_lessons": LEARNING_DIR / "recruiter_lessons.md",
    "successful_patterns": LEARNING_DIR / "successful_patterns.md",
    "weak_patterns": LEARNING_DIR / "weak_patterns.md",
}
