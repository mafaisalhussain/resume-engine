# Resume Engine -- Streamlit Web UI (Anime Sky Edition)
from __future__ import annotations

import json
import random
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

import streamlit as st

ROOT = Path(__file__).parent
JD_DIR = ROOT / "jd"
OUTPUTS_DIR = ROOT / "outputs"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GENERATE_STEPS = [
    "Load Knowledge Base", "Write Resume",
    "ATS Review", "Recruiter Review", "Self-Critique", "Learning Update",
]
OPTIMIZE_STEPS = [
    "Load Knowledge Base", "ATS Review",
    "Recruiter Review", "Self-Critique", "Learning Update",
]
STEP_MARKERS = {
    "KnowledgeLoader": "Load Knowledge Base",
    "ResumeWriterAgent": "Write Resume",
    "ATSReviewAgent": "ATS Review",
    "RecruiterReviewAgent": "Recruiter Review",
    "SelfCritiqueAgent": "Self-Critique",
    "LearningAgent": "Learning Update",
}

QUOTES = [
    ("If you don't take risks, you can't create a future.", "Monkey D. Luffy"),
    ("I'm going to be King of the Pirates!", "Monkey D. Luffy"),
    ("A dropout will beat a genius through hard work.", "Rock Lee"),
    ("Hard work is worthless for those that don't believe in themselves.", "Naruto Uzumaki"),
    ("People's dreams never die.", "Marshall D. Teach"),
    ("Push past your limits. That's how you get stronger.", "All Might"),
    ("I'll surpass all my limits.", "Rock Lee"),
    ("The true shame is not falling down, but never standing back up.", "Midoriya Izuku"),
    ("Whatever you lose, you'll find it again. What you throw away, you'll never get back.", "Kenshin Himura"),
    ("I don't want to conquer anything. I just think the guy with the most freedom in this ocean is the Pirate King.", "Monkey D. Luffy"),
]

SAMPLE_JD = """Software Engineer -- Cloud Infrastructure

We are looking for a Software Engineer to join our Cloud Infrastructure team.

Responsibilities:
- Design and implement scalable cloud-native systems on AWS/GCP
- Build and maintain CI/CD pipelines and DevOps tooling
- Collaborate with cross-functional teams to ship high-quality features
- Write clean, well-tested Python or Go services

Requirements:
- 2+ years of experience with cloud platforms (AWS, GCP, or Azure)
- Proficiency in Python or Go
- Experience with Kubernetes, Docker, and infrastructure-as-code (Terraform)
- Familiarity with distributed systems and microservices architecture
- Strong communication skills and ability to work in an agile environment

Nice to have:
- Experience with data pipelines or ML infrastructure
- Open-source contributions
- Knowledge of security best practices
"""

# Deterministic star positions via CSS box-shadow
_sr = random.Random(42)
_STAR_SHADOWS_SM = ", ".join(
    f"{_sr.randint(10,1900)}px {_sr.randint(10,980)}px "
    f"rgba(255,255,255,{_sr.uniform(0.3,0.8):.2f})"
    for _ in range(60)
)
_STAR_SHADOWS_MD = ", ".join(
    f"{_sr.randint(10,1900)}px {_sr.randint(10,980)}px "
    f"rgba(255,255,255,{_sr.uniform(0.4,0.9):.2f})"
    for _ in range(25)
)

# SVG icons (inline, no external URLs)
ICON_BRAIN = (
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="1.8">'
    '<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08'
    ' 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24A2.5 2.5 0 0 1 9.5 2Z"/>'
    '<path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08'
    ' 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24A2.5 2.5 0 0 0 14.5 2Z"/>'
    "</svg>"
)
ICON_TARGET = (
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="1.8">'
    '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>'
    "</svg>"
)
ICON_LATEX = (
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="1.8">'
    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
    '<polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>'
    '<line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>'
    "</svg>"
)
ICON_LIGHTNING = (
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FBBF24" stroke-width="1.8">'
    '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'
    "</svg>"
)

FEATURE_CARDS = [
    (ICON_BRAIN,     "AI-Powered",       "Advanced AI tailors your resume to match each job description perfectly."),
    (ICON_TARGET,    "ATS Optimized",    "Beat the bots. Score higher and reach real human recruiters."),
    (ICON_LATEX,     "LaTeX Beautiful",  "Generate clean, professional LaTeX resumes that stand out."),
    (ICON_LIGHTNING, "Lightning Fast",   "From job description to tailored resume in under 60 seconds."),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def _ollama_online() -> bool:
    try:
        urlopen("http://localhost:11434", timeout=2)
        return True
    except URLError:
        return False
    except Exception:
        return True


def _get_existing() -> list[str]:
    if not OUTPUTS_DIR.exists():
        return []
    return sorted(d.name for d in OUTPUTS_DIR.iterdir() if d.is_dir())


def _random_quote() -> tuple[str, str]:
    if "quote" not in st.session_state:
        st.session_state.quote = random.choice(QUOTES)
    return st.session_state.quote  # type: ignore[return-value]

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

GLOBAL_CSS = (
    "<style>"
    # Background
    ".stApp {"
    "  background: linear-gradient(160deg,"
    "    #04040f 0%, #090520 20%, #120b38 45%, #1e1055 65%, #2a1468 85%, #1a0a40 100%)"
    "  !important;"
    "}"
    "[data-testid='stAppViewContainer'], [data-testid='stMain'] {"
    "  background: transparent !important;"
    "}"
    # Stars
    ".stars-sm {"
    "  position: fixed; top: 0; left: 0; width: 1px; height: 1px;"
    "  background: transparent;"
    f" box-shadow: {_STAR_SHADOWS_SM};"
    "  border-radius: 50%; z-index: 0; pointer-events: none;"
    "  animation: twinkle 4s ease-in-out infinite alternate;"
    "}"
    ".stars-md {"
    "  position: fixed; top: 0; left: 0; width: 2px; height: 2px;"
    "  background: transparent;"
    f" box-shadow: {_STAR_SHADOWS_MD};"
    "  border-radius: 50%; z-index: 0; pointer-events: none;"
    "  animation: twinkle 6s ease-in-out infinite alternate-reverse;"
    "}"
    "@keyframes twinkle {"
    "  0% { opacity: 0.4; } 100% { opacity: 1; }"
    "}"
    # Moon
    ".moon {"
    "  position: fixed; top: 50px; right: 100px;"
    "  width: 110px; height: 110px; border-radius: 50%;"
    "  background: radial-gradient(circle at 38% 38%,"
    "    #fffae8 0%, #f0d898 40%, #c8a860 70%, transparent 100%);"
    "  box-shadow: 0 0 80px rgba(240,200,100,0.35), 0 0 30px rgba(255,240,180,0.2);"
    "  z-index: 0; pointer-events: none;"
    "}"
    # Top header bar
    "[data-testid='stHeader'] {"
    "  background: transparent !important;"
    "  border-bottom: none !important;"
    "}"
    # Sidebar
    "[data-testid='stSidebar'] {"
    "  background: rgba(8,5,28,0.85) !important;"
    "  border-right: 1px solid rgba(108,99,255,0.2) !important;"
    "  backdrop-filter: blur(20px) !important;"
    "}"
    "[data-testid='stSidebar'] > div:first-child {"
    "  padding-top: 0 !important;"
    "}"
    # Radio-based nav styling
    "[data-testid='stRadio'] > div { gap: 4px !important; }"
    "[data-testid='stRadio'] label {"
    "  display: flex !important; align-items: center !important;"
    "  padding: 10px 14px !important; border-radius: 10px !important;"
    "  cursor: pointer !important; transition: all 0.18s ease !important;"
    "  color: #6A7AA0 !important; font-weight: 500 !important; font-size: 14px !important;"
    "  width: 100% !important;"
    "}"
    "[data-testid='stRadio'] label:has(input:checked) {"
    "  background: linear-gradient(135deg, #6C63FF, #8B5CF6) !important;"
    "  color: white !important; box-shadow: 0 4px 15px rgba(108,99,255,0.4) !important;"
    "}"
    "[data-testid='stRadio'] label:hover:not(:has(input:checked)) {"
    "  background: rgba(108,99,255,0.12) !important; color: #C0C8E0 !important;"
    "}"
    "[data-testid='stRadio'] input[type='radio'] { display: none !important; }"
    "[data-testid='stRadio'] p { font-size: 14px !important; margin: 0 !important; }"
    # Text defaults
    "body, p, span, li { color: #D8D8F0 !important; }"
    # Headings
    "h1, h2, h3 { color: #E8E8FF !important; font-weight: 700 !important; }"
    # Primary button
    ".stButton > button[kind='primary'],"
    "[data-testid='stBaseButton-primary'] {"
    "  background: linear-gradient(135deg, #6C63FF 0%, #8B5CF6 100%) !important;"
    "  border: none !important; color: white !important;"
    "  font-weight: 700 !important; font-size: 14px !important;"
    "  letter-spacing: 0.5px !important; border-radius: 10px !important;"
    "  padding: 12px 20px !important;"
    "  box-shadow: 0 4px 20px rgba(108,99,255,0.4) !important;"
    "  transition: all 0.2s ease !important;"
    "}"
    ".stButton > button[kind='primary']:hover,"
    "[data-testid='stBaseButton-primary']:hover {"
    "  background: linear-gradient(135deg, #7C73FF 0%, #9B6CF6 100%) !important;"
    "  box-shadow: 0 6px 28px rgba(108,99,255,0.6), 0 0 20px rgba(139,92,246,0.3) !important;"
    "  transform: translateY(-2px) !important;"
    "}"
    # Secondary / download buttons
    ".stButton > button[kind='secondary'],"
    "[data-testid='stBaseButton-secondary'],"
    "[data-testid='stDownloadButton'] > button {"
    "  background: rgba(255,255,255,0.05) !important;"
    "  border: 1px solid rgba(108,99,255,0.35) !important;"
    "  color: #A0A8D0 !important; border-radius: 8px !important;"
    "  font-weight: 500 !important; transition: all 0.18s ease !important;"
    "}"
    "[data-testid='stDownloadButton'] > button:hover {"
    "  border-color: #6C63FF !important; color: #C8C0FF !important;"
    "  background: rgba(108,99,255,0.1) !important;"
    "}"
    # Glassmorphism containers
    "[data-testid='stVerticalBlockBorderWrapper'] {"
    "  background: rgba(255,255,255,0.04) !important;"
    "  border: 1px solid rgba(255,255,255,0.1) !important;"
    "  border-radius: 16px !important;"
    "  backdrop-filter: blur(20px) !important;"
    "}"
    # Inputs
    "[data-testid='stTextInput'] input,"
    "[data-testid='stTextArea'] textarea {"
    "  background: rgba(255,255,255,0.05) !important;"
    "  border: 1px solid rgba(108,99,255,0.25) !important;"
    "  color: #E0E0F8 !important; border-radius: 10px !important;"
    "  caret-color: #8B5CF6 !important;"
    "}"
    "[data-testid='stTextInput'] input:focus,"
    "[data-testid='stTextArea'] textarea:focus {"
    "  border-color: #6C63FF !important;"
    "  box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;"
    "}"
    "[data-testid='stTextInput'] input::placeholder,"
    "[data-testid='stTextArea'] textarea::placeholder { color: #3E4870 !important; }"
    # Selectbox
    "[data-testid='stSelectbox'] > div > div, [data-baseweb='select'] > div {"
    "  background: rgba(255,255,255,0.05) !important;"
    "  border-color: rgba(108,99,255,0.25) !important;"
    "  color: #E0E0F8 !important; border-radius: 10px !important;"
    "}"
    "[data-baseweb='select'] svg { fill: #8B5CF6 !important; }"
    "[data-baseweb='popover'] ul, [data-baseweb='menu'] {"
    "  background: #150D3A !important; border: 1px solid rgba(108,99,255,0.3) !important;"
    "}"
    "[data-baseweb='option']:hover { background: rgba(108,99,255,0.15) !important; }"
    # Metric cards
    "[data-testid='metric-container'] {"
    "  background: rgba(108,99,255,0.08) !important;"
    "  border: 1px solid rgba(108,99,255,0.2) !important;"
    "  border-top: 3px solid #6C63FF !important;"
    "  border-radius: 12px !important; padding: 16px 20px !important;"
    "}"
    "[data-testid='stMetricValue'] > div {"
    "  color: #A78BFA !important; font-size: 26px !important; font-weight: 700 !important;"
    "}"
    "[data-testid='stMetricLabel'] > div {"
    "  color: #6A7AA0 !important; font-size: 11px !important;"
    "  text-transform: uppercase !important; letter-spacing: 1px !important; font-weight: 600 !important;"
    "}"
    # Expanders
    "[data-testid='stExpander'] {"
    "  background: rgba(255,255,255,0.03) !important;"
    "  border: 1px solid rgba(108,99,255,0.2) !important; border-radius: 12px !important;"
    "}"
    "[data-testid='stExpander'] summary, [data-testid='stExpander'] summary p {"
    "  color: #A78BFA !important; font-weight: 600 !important;"
    "}"
    "[data-testid='stExpander'] svg { stroke: #8B5CF6 !important; fill: #8B5CF6 !important; }"
    # Alerts
    "[data-testid='stAlert'] {"
    "  background: rgba(255,255,255,0.04) !important;"
    "  border-left-color: #6C63FF !important; border-radius: 10px !important;"
    "}"
    "[data-testid='stAlert'] p { color: #D0D0F0 !important; }"
    # Tabs
    "[data-testid='stTabs'] [data-baseweb='tab-list'] {"
    "  background: rgba(255,255,255,0.04) !important; border-radius: 10px !important;"
    "  padding: 4px !important; border-bottom: none !important;"
    "  gap: 4px !important;"
    "}"
    "[data-testid='stTabs'] [data-baseweb='tab'] {"
    "  background: transparent !important; border: none !important;"
    "  color: #6A7AA0 !important; font-weight: 600 !important;"
    "  border-radius: 8px !important; padding: 8px 16px !important;"
    "}"
    "[data-testid='stTabs'] [aria-selected='true'] {"
    "  background: linear-gradient(135deg, #6C63FF, #8B5CF6) !important;"
    "  color: white !important;"
    "}"
    "[data-testid='stTabs'] [data-baseweb='tab-border'] { display: none !important; }"
    # Caption
    "[data-testid='stCaptionContainer'] p, .stCaption { color: #4A5A80 !important; }"
    # Divider
    "hr { border-color: rgba(108,99,255,0.2) !important; }"
    # Code blocks
    "[data-testid='stCode'] pre { background: rgba(0,0,0,0.4) !important; color: #C0C8E8 !important; }"
    # File uploader
    "[data-testid='stFileUploader'] {"
    "  background: rgba(255,255,255,0.03) !important;"
    "  border: 1px dashed rgba(108,99,255,0.3) !important; border-radius: 10px !important;"
    "}"
    # Scrollbar
    "::-webkit-scrollbar { width: 5px; height: 5px; }"
    "::-webkit-scrollbar-track { background: #04040f; }"
    "::-webkit-scrollbar-thumb { background: #6C63FF; border-radius: 3px; }"
    "::-webkit-scrollbar-thumb:hover { background: #8B5CF6; }"
    # Feature cards (custom)
    ".feat-card {"
    "  background: rgba(255,255,255,0.04);"
    "  border: 1px solid rgba(255,255,255,0.09);"
    "  border-radius: 14px; padding: 22px 18px;"
    "  backdrop-filter: blur(12px);"
    "  height: 100%;"
    "}"
    ".feat-icon { margin-bottom: 14px; }"
    ".feat-title { font-size: 15px; font-weight: 700; color: #E0E0FF; margin-bottom: 8px; }"
    ".feat-body { font-size: 13px; color: #6A7AA0; line-height: 1.55; }"
    # History cards
    ".hist-card {"
    "  background: rgba(255,255,255,0.04);"
    "  border: 1px solid rgba(108,99,255,0.18);"
    "  border-radius: 14px; padding: 20px 22px; margin-bottom: 14px;"
    "}"
    ".hist-company { font-size: 17px; font-weight: 700; color: #C8C0FF; margin-bottom: 4px; }"
    ".hist-date { font-size: 12px; color: #4A5A80; margin-bottom: 12px; }"
    ".hist-scores { display: flex; gap: 16px; }"
    ".hist-badge {"
    "  padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;"
    "}"
    ".badge-ats { background: rgba(108,99,255,0.15); color: #A78BFA; }"
    ".badge-rec { background: rgba(52,211,153,0.12); color: #34D399; }"
    ".badge-pass { background: rgba(52,211,153,0.15); color: #34D399; }"
    ".badge-fail { background: rgba(239,68,68,0.12); color: #F87171; }"
    # Preview pane
    ".preview-pane {"
    "  background: rgba(255,255,255,0.03);"
    "  border: 1px solid rgba(255,255,255,0.08);"
    "  border-radius: 14px; padding: 20px;"
    "  min-height: 460px;"
    "}"
    ".preview-badge {"
    "  display: inline-block; padding: 3px 10px; border-radius: 20px;"
    "  font-size: 11px; font-weight: 600; margin-right: 6px;"
    "}"
    ".badge-live { background: rgba(52,211,153,0.15); color: #34D399; }"
    ".badge-ai { background: rgba(139,92,246,0.2); color: #A78BFA; }"
    ".preview-empty {"
    "  text-align: center; padding: 60px 20px 30px 20px; color: #4A5A80;"
    "}"
    ".wireframe-line {"
    "  height: 10px; border-radius: 5px; margin-bottom: 8px;"
    "  background: rgba(108,99,255,0.1);"
    "}"
    # Quote banner
    ".quote-banner {"
    "  padding: 14px 20px 14px 22px;"
    "  background: rgba(108,99,255,0.08);"
    "  border-left: 3px solid #6C63FF;"
    "  border-radius: 0 10px 10px 0;"
    "  margin-bottom: 24px;"
    "}"
    ".quote-text { font-style: italic; color: #C0C0E0; font-size: 14px; line-height: 1.6; }"
    ".quote-author { text-align: right; color: #6C63FF; font-size: 12px; font-weight: 600; margin-top: 6px; }"
    # Coming soon badge
    ".coming-soon {"
    "  display: inline-block; padding: 4px 12px;"
    "  background: rgba(251,191,36,0.15); color: #FBBF24;"
    "  border-radius: 20px; font-size: 12px; font-weight: 600;"
    "}"
    # Trust line
    ".trust-line { text-align: center; color: #3A4870; font-size: 12px; margin-top: 10px; }"
    "</style>"
)

# ---------------------------------------------------------------------------
# Tracker
# ---------------------------------------------------------------------------

def _render_tracker(steps: list[str], completed: set[str], current: str | None) -> str:
    rows = []
    for step in steps:
        if step in completed:
            icon = "&#x2B50;"
            cls = "tr-done"
        elif step == current:
            icon = "&#x1F525;"
            cls = "tr-run"
        else:
            icon = "&#x25CB;"
            cls = "tr-wait"
        rows.append(
            f'<div class="tr-step {cls}">'
            f'<span class="tr-icon">{icon}</span>'
            f'<span>{step}</span>'
            f"</div>"
        )
    inner = "".join(rows)
    return (
        "<style>"
        ".tr-wrap{display:flex;flex-direction:column;gap:5px;padding:14px 16px;"
        "background:rgba(4,4,15,0.6);border:1px solid rgba(108,99,255,0.25);"
        "border-radius:12px;font-family:'Segoe UI',system-ui,sans-serif;}"
        ".tr-step{display:flex;align-items:center;gap:11px;font-size:14px;"
        "padding:8px 11px;border-radius:8px;}"
        ".tr-icon{font-size:16px;min-width:20px;text-align:center;}"
        ".tr-done{color:#A78BFA;background:rgba(108,99,255,0.1);}"
        ".tr-wait{color:#2E3A5E;background:transparent;}"
        ".tr-run{color:#FB923C;background:rgba(251,146,60,0.1);font-weight:700;"
        "animation:trfire 1.2s ease-in-out infinite;}"
        "@keyframes trfire{0%,100%{opacity:1;transform:scale(1);}"
        "50%{opacity:0.55;transform:scale(1.01);}}"
        "</style>"
        f'<div class="tr-wrap">{inner}</div>'
    )

# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

def _run_pipeline(
    cmd: list[str],
    steps: list[str],
    tracker_ph: "st.delta_generator.DeltaGenerator",
    log_ph: "st.delta_generator.DeltaGenerator",
) -> tuple[int, list[str]]:
    completed: set[str] = set()
    current: str | None = None
    log_lines: list[str] = []

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=str(ROOT),
    )

    for raw in proc.stdout:  # type: ignore[union-attr]
        line = raw.rstrip()
        log_lines.append(line)

        if "[STEP_START]" in line:
            cls = line.split("[STEP_START]")[1].strip()
            mapped = STEP_MARKERS.get(cls)
            if mapped:
                if current and current not in completed:
                    completed.add(current)
                current = mapped

        tracker_ph.markdown(_render_tracker(steps, completed, current), unsafe_allow_html=True)
        tail = log_lines[-18:] if len(log_lines) > 18 else log_lines
        log_ph.code("\n".join(tail), language=None)

    proc.wait()
    if current:
        completed.add(current)
    tracker_ph.markdown(_render_tracker(steps, completed, None), unsafe_allow_html=True)
    return proc.returncode, log_lines

# ---------------------------------------------------------------------------
# Shared widgets
# ---------------------------------------------------------------------------

def _hero(subtitle: str = "AI-powered. ATS-optimized. Yours.") -> None:
    quote, speaker = _random_quote()
    st.markdown(
        "<div style='text-align:center;padding:32px 0 8px 0;'>"
        "<h1 style='font-size:clamp(26px,3.5vw,42px);font-weight:800;"
        "color:#E8E8FF;line-height:1.25;margin-bottom:10px;"
        "text-shadow:0 0 40px rgba(108,99,255,0.4);'>"
        "Craft a resume that "
        "<span style='background:linear-gradient(90deg,#E040FB,#6C63FF);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
        "background-clip:text;'>sails</span>"
        " past the competition."
        "</h1>"
        f"<p style='color:#6A7AA0;font-size:16px;margin-bottom:20px;'>{subtitle}</p>"
        f'<div class="quote-banner" style="max-width:620px;margin:0 auto 0 auto;">'
        f'<div class="quote-text">&ldquo;{quote}&rdquo;</div>'
        f'<div class="quote-author">&mdash; {speaker}</div>'
        f"</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def _preview_placeholder() -> str:
    return (
        '<div class="preview-pane">'
        '<div style="margin-bottom:10px;">'
        '<span class="preview-badge badge-live">&#x25CF; Live Preview</span>'
        '<span class="preview-badge badge-ai">AI Generated</span>'
        "</div>"
        '<div class="preview-empty">'
        '<div style="font-size:42px;margin-bottom:14px;">&#x1F4C4;</div>'
        '<div style="font-size:15px;font-weight:600;color:#5A6A90;margin-bottom:6px;">'
        "Your resume will appear here"
        "</div>"
        '<div style="font-size:13px;color:#3A4870;">'
        "Generate a resume to see the live preview"
        "</div>"
        "</div>"
        '<div style="padding:0 8px;">'
        '<div class="wireframe-line" style="width:55%;background:rgba(108,99,255,0.12);"></div>'
        '<div class="wireframe-line" style="width:35%;background:rgba(108,99,255,0.07);"></div>'
        '<div style="margin:14px 0 6px 0;height:1px;background:rgba(108,99,255,0.1);"></div>'
        '<div class="wireframe-line" style="background:rgba(108,99,255,0.08);"></div>'
        '<div class="wireframe-line" style="width:90%;background:rgba(108,99,255,0.06);"></div>'
        '<div class="wireframe-line" style="width:75%;background:rgba(108,99,255,0.08);"></div>'
        '<div style="margin:12px 0 6px 0;height:1px;background:rgba(108,99,255,0.08);"></div>'
        '<div class="wireframe-line" style="background:rgba(108,99,255,0.07);"></div>'
        '<div class="wireframe-line" style="width:85%;background:rgba(108,99,255,0.05);"></div>'
        "</div>"
        "</div>"
    )


def _feature_cards() -> None:
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    for col, (icon, title, body) in zip([c1, c2, c3, c4], FEATURE_CARDS):
        with col:
            st.markdown(
                f'<div class="feat-card">'
                f'<div class="feat-icon">{icon}</div>'
                f'<div class="feat-title">{title}</div>'
                f'<div class="feat-body">{body}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def render_generate_page(ollama_ok: bool) -> None:
    _hero()

    form_col, prev_col = st.columns([1.15, 1], gap="medium")

    with form_col:
        with st.container(border=True):
            st.markdown("#### &#x2693; Generate Resume", unsafe_allow_html=True)

            company = st.text_input("Company Name", placeholder="e.g. Google, DHS, Loomai", key="gen_company")
            slug = _slugify(company) if company else ""
            if slug:
                st.caption(f"Slug: `{slug}`")

            jd_text = st.text_area(
                "Job Description",
                height=230,
                placeholder="Paste the full job description here...",
                key="gen_jd",
            )
            char_count = len(jd_text)
            st.caption(f"{char_count:,} / 6,000 characters")

            ba, bb, bc = st.columns(3)
            with ba:
                uploaded = st.file_uploader(
                    "Upload JD", type=["md", "txt", "pdf"],
                    label_visibility="collapsed", key="gen_upload",
                )
                if uploaded:
                    st.session_state.gen_jd = uploaded.read().decode("utf-8", errors="replace")
                    st.rerun()
            with bb:
                if st.button("Upload JD", key="gen_upload_btn", use_container_width=True):
                    pass  # trigger file_uploader above
            with bc:
                if st.button("Sample JD", key="gen_sample", use_container_width=True):
                    st.session_state.gen_jd = SAMPLE_JD
                    st.rerun()

            can_run = bool(company and jd_text and ollama_ok)
            run_btn = st.button(
                "&#x2693; Set Sail & Generate",
                type="primary",
                disabled=not can_run,
                use_container_width=True,
                key="gen_run",
            )
            st.markdown('<div class="trust-line">&#x1F512; Your data stays local. Never shared.</div>', unsafe_allow_html=True)
            if not ollama_ok:
                st.warning("Ollama offline. Start with `ollama serve`.")

    with prev_col:
        preview_ph = st.empty()
        tracker_ph = st.empty()
        log_ph = st.empty()

        # Initialize preview
        if "gen_result" not in st.session_state:
            preview_ph.markdown(_preview_placeholder(), unsafe_allow_html=True)

    if run_btn:
        # Clear old result, show tracker in preview pane
        preview_ph.empty()
        JD_DIR.mkdir(exist_ok=True)
        jd_file = JD_DIR / f"{slug}.md"
        jd_file.write_text(jd_text, encoding="utf-8")

        cmd = [sys.executable, "-u", "main.py", "generate",
               "--jd", str(jd_file), "--company", company, "--verbose"]

        with prev_col:
            st.markdown(
                '<div style="margin-bottom:8px;">'
                '<span class="preview-badge badge-live">&#x25CF; Live</span>'
                '<span class="preview-badge badge-ai">Running</span>'
                "</div>",
                unsafe_allow_html=True,
            )

        returncode, log_lines = _run_pipeline(cmd, GENERATE_STEPS, tracker_ph, log_ph)

        if returncode == 0:
            st.session_state.gen_result = {"slug": slug, "log": log_lines}
        else:
            st.error("Pipeline failed. Check the log above.")

    # Show result if available
    if st.session_state.get("gen_result", {}).get("slug") == (slug if company else ""):
        slug_r = st.session_state.gen_result["slug"]

        meta_path = OUTPUTS_DIR / slug_r / f"{slug_r}_metadata.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            ats = meta.get("ats_score", 0)
            rec = meta.get("recruiter_score", 0)
            combined = ats + rec

            st.markdown("---")
            st.markdown("#### Scores")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("ATS Score", f"{ats} / 80")
            mc2.metric("Recruiter Score", f"{rec} / 80")
            mc3.metric("Combined", f"{combined} / 160", delta="PASS" if combined >= 80 else "FAIL")

        score_path = OUTPUTS_DIR / slug_r / f"{slug_r}_score_report.md"
        resume_path = OUTPUTS_DIR / slug_r / f"{slug_r}_resume.md"

        if resume_path.exists():
            latex_src = resume_path.read_text(encoding="utf-8")
            # Update right pane with resume preview
            with prev_col:
                tracker_ph.empty()
                log_ph.empty()
                preview_ph.markdown(
                    '<div class="preview-pane" style="overflow:auto;max-height:500px;">'
                    '<div style="margin-bottom:10px;">'
                    '<span class="preview-badge badge-live">&#x25CF; Live Preview</span>'
                    '<span class="preview-badge badge-ai">AI Generated</span>'
                    "</div></div>",
                    unsafe_allow_html=True,
                )
                st.code(latex_src, language="latex", line_numbers=True)

            dl1, dl2 = st.columns(2)
            dl1.download_button(
                "Download Resume (.tex)",
                data=latex_src,
                file_name=f"{slug_r}_resume.tex",
                mime="text/plain",
                use_container_width=True,
            )
            if score_path.exists():
                dl2.download_button(
                    "Download Score Report",
                    data=score_path.read_text(encoding="utf-8"),
                    file_name=f"{slug_r}_score_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        if score_path.exists():
            with st.expander("Score Report"):
                st.markdown(score_path.read_text(encoding="utf-8"))

    _feature_cards()


def render_optimize_page(ollama_ok: bool) -> None:
    _hero("Review an existing resume. Level up its scores. Update the learning files.")

    existing = _get_existing()
    if not existing:
        st.warning("No generated resumes found in `outputs/`. Run **Generate** mode first.")
        return

    form_col, prev_col = st.columns([1.15, 1], gap="medium")

    with form_col:
        with st.container(border=True):
            st.markdown("#### &#x267B; Optimize Resume", unsafe_allow_html=True)

            selected_slug = st.selectbox("Select Company", existing, key="opt_slug")

            jd_prefill = ""
            jd_cand = JD_DIR / f"{selected_slug}.md"
            if jd_cand.exists() and "opt_jd" not in st.session_state:
                jd_prefill = jd_cand.read_text(encoding="utf-8")

            jd_text = st.text_area(
                "Job Description",
                value=jd_prefill,
                height=230,
                placeholder="Paste the full job description here...",
                key="opt_jd",
            )
            st.caption(f"{len(jd_text):,} / 6,000 characters")

            resume_file = OUTPUTS_DIR / selected_slug / f"{selected_slug}_resume.md"
            if resume_file.exists():
                st.caption(f"Resume: `{resume_file.relative_to(ROOT)}`")
            else:
                st.error(f"Resume file not found: `{resume_file}`")

            can_run = bool(jd_text and ollama_ok and resume_file.exists())
            run_btn = st.button(
                "&#x267B; Train & Improve",
                type="primary",
                disabled=not can_run,
                use_container_width=True,
                key="opt_run",
            )
            st.markdown('<div class="trust-line">&#x1F512; Your data stays local. Never shared.</div>', unsafe_allow_html=True)
            if not ollama_ok:
                st.warning("Ollama offline. Start with `ollama serve`.")

    with prev_col:
        tracker_ph = st.empty()
        log_ph = st.empty()
        if not run_btn:
            st.markdown(_preview_placeholder(), unsafe_allow_html=True)

    if run_btn:
        JD_DIR.mkdir(exist_ok=True)
        jd_file = JD_DIR / f"{selected_slug}.md"
        jd_file.write_text(jd_text, encoding="utf-8")

        cmd = [sys.executable, "-u", "main.py", "optimize",
               "--resume", str(resume_file),
               "--jd", str(jd_file),
               "--verbose"]

        returncode, log_lines = _run_pipeline(cmd, OPTIMIZE_STEPS, tracker_ph, log_ph)
        full_output = "\n".join(log_lines)

        if returncode == 0:
            st.success("Training complete -- learning files updated!")

            ats_m = re.search(r"ATS Score\s*:\s*(\d+)/80", full_output)
            rec_m = re.search(r"Recruiter Score\s*:\s*(\d+)/80", full_output)
            if ats_m and rec_m:
                ats, rec = int(ats_m.group(1)), int(rec_m.group(1))
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("ATS Score", f"{ats} / 80")
                mc2.metric("Recruiter Score", f"{rec} / 80")
                mc3.metric("Combined", f"{ats + rec} / 160", delta="PASS" if (ats + rec) >= 80 else "FAIL")

            with st.expander("Full Output Log"):
                st.code(full_output, language=None)
        else:
            st.error("Pipeline failed. See log above.")


def render_history_page() -> None:
    st.markdown(
        "<h2 style='margin-bottom:4px;'>&#x23F1; History</h2>"
        "<p style='color:#4A5A80;margin-bottom:24px;'>All past resume generation runs.</p>",
        unsafe_allow_html=True,
    )

    existing = _get_existing()
    if not existing:
        st.info("No runs yet. Go to **Generate** to create your first resume.")
        return

    col_a, col_b = st.columns(2, gap="medium")
    for i, slug in enumerate(reversed(existing)):
        col = col_a if i % 2 == 0 else col_b
        meta_path = OUTPUTS_DIR / slug / f"{slug}_metadata.json"
        resume_path = OUTPUTS_DIR / slug / f"{slug}_resume.md"
        score_path = OUTPUTS_DIR / slug / f"{slug}_score_report.md"

        meta = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        ats = meta.get("ats_score", "-")
        rec = meta.get("recruiter_score", "-")
        combined = (ats + rec) if isinstance(ats, int) and isinstance(rec, int) else "-"
        ts = meta.get("timestamp", "")
        date_str = ts[:10] if ts else "Unknown date"
        passes = isinstance(combined, int) and combined >= 80

        with col:
            st.markdown(
                f'<div class="hist-card">'
                f'<div class="hist-company">&#x2693; {slug.replace("-", " ").title()}</div>'
                f'<div class="hist-date">{date_str}</div>'
                f'<div class="hist-scores">'
                f'<span class="hist-badge badge-ats">ATS {ats}/80</span>'
                f'<span class="hist-badge badge-rec">Recruiter {rec}/80</span>'
                f'<span class="hist-badge {"badge-pass" if passes else "badge-fail"}">'
                f'{"PASS" if passes else "FAIL"}'
                f"</span>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if resume_path.exists():
                with st.expander(f"View {slug}"):
                    latex_src = resume_path.read_text(encoding="utf-8")
                    st.code(latex_src, language="latex")
                    dl1, dl2 = st.columns(2)
                    dl1.download_button(
                        "Download .tex",
                        data=latex_src,
                        file_name=f"{slug}_resume.tex",
                        mime="text/plain",
                        key=f"dl_tex_{slug}",
                        use_container_width=True,
                    )
                    if score_path.exists():
                        dl2.download_button(
                            "Download Report",
                            data=score_path.read_text(encoding="utf-8"),
                            file_name=f"{slug}_score_report.md",
                            mime="text/markdown",
                            key=f"dl_rep_{slug}",
                            use_container_width=True,
                        )


def render_settings_page(ollama_ok: bool) -> None:
    st.markdown(
        "<h2 style='margin-bottom:4px;'>&#x2699; Settings</h2>"
        "<p style='color:#4A5A80;margin-bottom:24px;'>App configuration and status.</p>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("**Ollama Status**")
        if ollama_ok:
            st.success("Ollama is online at `http://localhost:11434`")
        else:
            st.error("Ollama is offline. Start with `ollama serve`.")

        st.markdown("**Model Configuration**")
        st.info(
            "Edit model names in `engine/config.py`:\n"
            "- `MODEL_STRONG` -- used by complex agents (writer, critique)\n"
            "- `MODEL_FAST` -- used by mechanical agents (ATS, recruiter)\n"
            "- Run `ollama list` to see available models."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            "**Advanced Features** "
            '<span class="coming-soon">Coming Soon</span>',
            unsafe_allow_html=True,
        )
        for feature in ["Custom prompt editor", "Template library", "Score analytics dashboard", "Multi-company batch generation"]:
            st.markdown(f"- {feature}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Resume Engine",
    page_icon="document",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject global CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Inject stars + moon
st.markdown(
    '<div class="stars-sm"></div>'
    '<div class="stars-md"></div>'
    '<div class="moon"></div>',
    unsafe_allow_html=True,
)

ollama_ok = _ollama_online()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    # Logo
    st.markdown(
        "<div style='padding:22px 16px 16px 16px;'>"
        "<div style='display:flex;align-items:center;gap:10px;margin-bottom:4px;'>"
        "<span style='font-size:24px;'>&#x2693;</span>"
        "<div>"
        "<div style='font-size:17px;font-weight:800;color:#E8E8FF;letter-spacing:1px;'>RESUME ENGINE</div>"
        "<div style='font-size:11px;color:#4A5A80;'>Conquer every job like Luffy</div>"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Navigation (radio styled as nav pills via CSS)
    page = st.radio(
        "nav",
        ["Generate", "Optimize", "History", "Settings"],
        label_visibility="collapsed",
        key="page",
    )

    st.divider()

    # Ollama status badge
    if ollama_ok:
        st.markdown(
            "<div style='display:flex;align-items:center;gap:8px;"
            "background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);"
            "border-radius:8px;padding:8px 12px;'>"
            "<span style='color:#34D399;'>&#x25CF;</span>"
            "<span style='color:#34D399;font-size:13px;font-weight:600;'>Ollama online</span>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='display:flex;align-items:center;gap:8px;"
            "background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);"
            "border-radius:8px;padding:8px 12px;'>"
            "<span style='color:#F87171;'>&#x25CF;</span>"
            "<span style='color:#F87171;font-size:13px;font-weight:600;'>Ollama offline</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Run: `ollama serve`")

    # Spacer + user profile at bottom
    st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='padding:12px;background:rgba(108,99,255,0.08);"
        "border:1px solid rgba(108,99,255,0.15);border-radius:10px;"
        "display:flex;align-items:center;gap:10px;'>"
        "<div style='width:36px;height:36px;border-radius:50%;"
        "background:linear-gradient(135deg,#6C63FF,#E040FB);"
        "display:flex;align-items:center;justify-content:center;"
        "font-size:15px;font-weight:700;color:white;flex-shrink:0;'>M</div>"
        "<div>"
        "<div style='font-size:13px;font-weight:600;color:#C8C0FF;'>Faisal</div>"
        "<div style='font-size:11px;color:#4A5A80;'>Straw Hat Pirates</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------

if page == "Generate":
    render_generate_page(ollama_ok)
elif page == "Optimize":
    render_optimize_page(ollama_ok)
elif page == "History":
    render_history_page()
else:
    render_settings_page(ollama_ok)
