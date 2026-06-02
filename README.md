# Resume Engine

**AI-powered, self-improving LaTeX resume generator — fully local, no API keys needed.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/LLM-Ollama-black?logo=ollama)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Personal%20Project-orange)

---

> **⚠️ Use at your own risk.**
> This is a **personal project**, not an official resume generation service.
> It is not affiliated with any company, hiring platform, ATS vendor, or recruiter tool.
> AI-generated content should always be reviewed carefully before submission to any employer.
> The author makes no guarantees about resume quality, ATS scores, or job outcomes.
> **Use it as a tool to accelerate your own work, not as a replacement for your judgment.**

---

> **💬 Feedback is genuinely appreciated!**
> If you use this tool, run into bugs, or have ideas to make it better — please open a
> [GitHub Issue](../../issues) or start a [Discussion](../../discussions).
> This is a personal project built for fun and utility, and every piece of feedback helps.

---

## What It Does

Resume Engine takes your personal knowledge base (your background, projects, skills) and a
target job description, then runs a multi-agent AI pipeline to produce a tailored,
ATS-optimized LaTeX resume. It scores the result, critiques it, iterates to improve it, and
learns from every run.

```
You paste a job description
        |
        v
[ Knowledge Base ] --> [ Multi-Agent Pipeline ] --> [ LaTeX Resume ]
                                                            |
                                         [ ATS Score + Recruiter Score + Critique ]
                                                            |
                                              [ Self-improve up to 5x ]
                                                            |
                                         [ Learning files updated for next run ]
```

---

## Features

- **Fully local** — runs entirely on your machine via Ollama. No API keys, no cloud calls, no data sent anywhere.
- **Multi-agent scoring** — ATS compliance checker, recruiter appeal reviewer, and an adversarial self-critic all score the resume independently.
- **Iterative improvement loop** — the writer, ATS reviewer, and recruiter reviewer loop up to 5 times until the combined score threshold is met.
- **Self-learning** — after each optimize run, lessons are extracted and stored. Future runs automatically read these lessons to avoid repeating mistakes.
- **LaTeX output** — compile with `pdflatex` or upload directly to Overleaf for a polished PDF.
- **Streamlit web UI** — anime-sky themed, with a live pipeline progress tracker and history page.
- **CLI mode** — run from the terminal for scripting and automation.

---

## How It's Built

### Architecture

The system is organized as a knowledge-base-driven multi-agent pipeline with no external dependencies beyond Ollama.

```
engine/
├── agents/
│   ├── base_agent.py             Base class with retry logic and JSON parsing
│   ├── resume_writer_agent.py    Writes the full LaTeX resume
│   ├── ats_review_agent.py       Scores ATS compliance (0-80)
│   ├── recruiter_review_agent.py Scores recruiter appeal (0-80)
│   ├── self_critique_agent.py    Adversarial final review
│   └── learning_agent.py         Extracts lessons for future runs
├── pipelines/
│   ├── generate_pipeline.py      Orchestrates generate + iterative loop
│   └── optimize_pipeline.py      Runs review agents on an existing resume
├── prompts/                      System prompts for each agent (.txt files)
├── config.py                     Model names, paths, thresholds
├── models.py                     Pydantic data models
├── knowledge_loader.py           Reads the knowledge base into memory
└── output_writer.py              Writes outputs/ and learning files

knowledge/
├── profile.md                    YOUR background (single source of truth — gitignored)
├── projects/                     Detailed project write-ups
├── frameworks/                   Rules the agents enforce (ATS, evidence classification, etc.)
├── metrics/                      Allowed quantified claims (to prevent hallucination)
├── action_verbs.md               Verb taxonomy for resume bullets
└── learning/                     Auto-appended lesson files (gitignored)
```

### Tech Stack

| Layer | Tool |
|---|---|
| LLM inference | [Ollama](https://ollama.com) — runs models locally |
| LLM model | `qwen3.5:9b` (customized via `Modelfile`) |
| Agent framework | Custom Python — intentionally no LangChain |
| Data models | [Pydantic v2](https://docs.pydantic.dev) |
| LLM API client | [OpenAI SDK](https://github.com/openai/openai-python) (Ollama-compatible endpoint) |
| Web UI | [Streamlit](https://streamlit.io) |
| Resume output | LaTeX (pdflatex-compatible) |
| Knowledge base | Markdown files |

### Agent Pipeline Detail

1. **KnowledgeLoader** — reads all markdown files from `knowledge/` into a single cache string injected into every agent's context.
2. **ResumeWriterAgent** — receives the JD + candidate profile + any revision instructions from the previous iteration. Outputs raw LaTeX.
3. **ATSReviewAgent** — parses the LaTeX and JD, produces a structured score (0–80) with keyword analysis, violations, and fabrication flags.
4. **RecruiterReviewAgent** — scores recruiter appeal across 8 dimensions (0–10 each, total 0–80): narrative clarity, impact quantification, relevance, etc.
5. **SelfCritiqueAgent** — adversarial final review that surfaces the honest weaknesses and interview risks.
6. **LearningAgent** — extracts lessons from the review scores and appends them to the four learning files.

The generate loop runs Writer → ATS → Recruiter up to **5 iterations**, stopping early when ATS + Recruiter ≥ 80 combined and no fabrication flags are raised. The best-scoring iteration is saved.

---

## Prerequisites

- **Python 3.10+**
- **Ollama** — [download here](https://ollama.com)
- **pdflatex** (optional) — to compile the LaTeX output to PDF. Or use [Overleaf](https://overleaf.com) (free, paste the `.tex` file).

---

## Installation & Setup

### 1. Install Ollama and pull the model

```bash
# Install Ollama from https://ollama.com, then:
ollama pull qwen3.5:9b

# Build the custom model with the project's Modelfile
ollama create resume-engine -f Modelfile
```

### 2. Clone the repository

```bash
git clone https://github.com/mafaisalhussain/resume-engine.git
cd resume-engine
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt       # core pipeline
pip install -r requirements_ui.txt    # only needed for the web UI
```

### 4. Set up your knowledge base

```bash
# Create your personal profile from the provided template
cp knowledge/profile_template.md knowledge/profile.md

# Open knowledge/profile.md and fill in your real information:
# - Contact details (name, email, phone, LinkedIn, GitHub)
# - Education history
# - Work experience with quantified bullet points
# - Skills
# - Certifications
```

The more detail you put into `profile.md`, the better the resumes will be. The AI reads this file as the single source of truth about you.

You can also add detailed project write-ups to `knowledge/projects/` — one file per project, as much detail as possible. The agent will select the most relevant ones for each JD.

### 5. Create a job description file

Save the job description as a `.md` file in the `jd/` directory:

```bash
# Use the included example to test:
# jd/example_software_engineer.md

# For a real run, save the JD text you're targeting:
# jd/google_swe.md
```

---

## Running the App

### Web UI (recommended)

```bash
# Start Ollama in a separate terminal
ollama serve

# Launch the web app
streamlit run app.py
# Opens at http://localhost:8501
```

The UI has four pages accessible from the left sidebar:
- **Generate** — paste a JD, click "Set Sail & Generate", watch the live pipeline tracker
- **Optimize** — select an existing resume and run the review + learning update
- **History** — view and download all past runs
- **Settings** — Ollama status and configuration info

### CLI

```bash
# Start Ollama
ollama serve

# Generate a new resume
python main.py generate --jd jd/example_software_engineer.md --company "Example Corp"

# With verbose token logging
python main.py generate --jd jd/google_swe.md --company "Google" --verbose

# Run the optimize + learning update on an existing resume
python main.py optimize \
  --resume outputs/google/google_resume.md \
  --jd jd/google_swe.md
```

---

## Output Files

Every `generate` run creates a folder under `outputs/<company-slug>/` with three files:

| File | Contents |
|---|---|
| `<slug>_resume.md` | Pure LaTeX source — rename to `.tex` and compile with `pdflatex` |
| `<slug>_score_report.md` | Full ATS + recruiter + critique scores and feedback |
| `<slug>_metadata.json` | Run metadata (timestamp, model, scores, keyword matches) |

The `outputs/` directory is gitignored — your generated resumes stay on your machine only.

---

## Customizing the Model

Edit `engine/config.py` to change which Ollama model is used:

```python
MODEL_STRONG = "resume-engine"   # complex agents (writer, critique)
MODEL_FAST   = "resume-engine"   # mechanical agents (ATS, recruiter)
```

Any model available via `ollama list` works. Larger models generally produce better resumes
but take longer. The included `Modelfile` sets a 32K context window and disables thinking
mode for clean output.

---

## Project Layout

```
resume-engine/
├── app.py                    Streamlit web UI
├── main.py                   CLI entry point
├── Modelfile                 Custom Ollama model definition
├── requirements.txt          Core dependencies (openai, pydantic)
├── requirements_ui.txt       UI dependency (streamlit)
├── engine/                   All agent and pipeline code
├── knowledge/
│   ├── profile_template.md   Template — copy to profile.md and fill in your info
│   ├── projects/             Detailed write-ups for each of your projects
│   ├── frameworks/           Rules the agents enforce
│   ├── metrics/              Allowed quantified claims
│   └── action_verbs.md       Resume verb taxonomy
└── jd/
    └── example_software_engineer.md   Sample JD to test with
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

Built with [Ollama](https://ollama.com), [Streamlit](https://streamlit.io), and
[Pydantic](https://docs.pydantic.dev). Inspired by the idea that the job search grind
deserves better tooling.

> *"If you don't take risks, you can't create a future."* — Monkey D. Luffy
