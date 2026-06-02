from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Evidence classification ────────────────────────────────────────────────

class EvidenceLabel(str, Enum):
    DIRECT = "DIRECT"
    ADJACENT = "ADJACENT"
    TRANSFERABLE = "TRANSFERABLE"
    UNSUPPORTED = "UNSUPPORTED"
    HARD_GAP = "HARD_GAP"


# ── Knowledge base ─────────────────────────────────────────────────────────

class LearningContext(BaseModel):
    ats_lessons: str = ""
    recruiter_lessons: str = ""
    successful_patterns: str = ""
    weak_patterns: str = ""


class KnowledgeBase(BaseModel):
    profile_md: str
    action_verbs_md: str
    metrics_md: str
    ats_compliance_md: str
    resume_structure_md: str
    vocabulary_bridges_md: str
    evidence_classification_md: str
    fluff_blacklist_md: str
    prohibited_items_md: str
    projects: dict[str, str]  # filename stem -> content
    learning_context: LearningContext = Field(default_factory=LearningContext)


# ── Candidate profile ──────────────────────────────────────────────────────

class CandidateProfile(BaseModel):
    name: str
    email: str
    phone: str
    linkedin: str
    github: str
    location: str
    education: list[dict[str, Any]]
    experiences: list[dict[str, Any]]
    projects: list[dict[str, Any]]
    skills: dict[str, list[str]]
    certifications: list[str]
    anchored_metrics: list[dict[str, Any]]


# ── Job intelligence ───────────────────────────────────────────────────────

class JobIntelligenceProfile(BaseModel):
    company_name: str
    role_title: str
    role_type: str  # "ml_engineering" | "data_science" | "cloud_devops" | "research" | "ai_product"
    must_have_keywords: list[str]
    nice_to_have_keywords: list[str]
    prohibited_keywords: list[str] = Field(default_factory=list)
    domain_signals: list[str]
    tone: str  # "startup" | "enterprise" | "government" | "research"
    experience_level: str  # "intern" | "early_career" | "mid"
    red_flags: list[str] = Field(default_factory=list)
    summary_for_agents: str


# ── Gap coverage ───────────────────────────────────────────────────────────

class EvidenceClaim(BaseModel):
    claim_text: str
    label: EvidenceLabel
    kb_citation: str | None = None
    fabrication_risk: str | None = None


class GapItem(BaseModel):
    jd_requirement: str
    candidate_evidence: str | None
    evidence_label: EvidenceLabel
    coverage_strategy: str
    kb_citation: str | None = None


class GapCoverageMap(BaseModel):
    covered_gaps: list[GapItem]
    partial_gaps: list[GapItem]
    hard_gaps: list[GapItem]
    claim_ledger: list[EvidenceClaim]
    coverage_score: float  # 0.0-1.0


# ── Resume strategy ────────────────────────────────────────────────────────

class ProjectSelection(BaseModel):
    project_name: str
    relevance_score: int  # 1-10
    selected_bullets: list[str]
    jd_keywords_matched: list[str]


class ExperienceSelection(BaseModel):
    company: str
    role: str
    date_range: str
    selected_bullets: list[str]
    jd_keywords_matched: list[str]


class ResumeStrategy(BaseModel):
    summary_angle: str
    projects_ordered: list[ProjectSelection]
    experiences_ordered: list[ExperienceSelection]
    skills_to_highlight: list[str]
    keywords_to_weave: list[str]
    section_emphasis: dict[str, str]
    page_budget: str
    strategy_rationale: str


# ── ATS evaluation ─────────────────────────────────────────────────────────

class ATSViolation(BaseModel):
    rule_id: str
    description: str
    location: str
    severity: str  # "FAIL" | "WARN"


class ATSScore(BaseModel):
    score: int  # 0-80
    violations: list[ATSViolation]
    keyword_hits: list[str]
    keyword_misses: list[str]
    fabrication_flags: list[str]
    passes: bool
    revision_instructions: str


# ── Recruiter evaluation ───────────────────────────────────────────────────

class RecruiterDimension(BaseModel):
    dimension_id: str  # D1-D8
    dimension_name: str
    score: int  # 0-10
    rationale: str
    improvement_suggestion: str | None = None


class RecruiterScore(BaseModel):
    dimensions: list[RecruiterDimension]
    total_score: int  # 0-80
    overall_assessment: str
    top_strengths: list[str]
    top_weaknesses: list[str]
    passes: bool
    revision_instructions: str


# ── Self-critique ──────────────────────────────────────────────────────────

class SelfCritiqueReport(BaseModel):
    honest_weaknesses: list[str]
    interview_risks: list[str]
    strongest_elements: list[str]
    final_recommendation: str  # "APPROVE" | "REVISE"
    confidence_score: int  # 0-100


# ── Outputs ────────────────────────────────────────────────────────────────

class ScoreReport(BaseModel):
    ats_score: ATSScore
    recruiter_score: RecruiterScore
    self_critique: SelfCritiqueReport
    combined_score: int
    iteration_count: int
    generation_timestamp: str


class ResumeMetadata(BaseModel):
    company_slug: str
    company_name: str
    role_title: str
    jd_path: str
    generation_timestamp: str
    model_used: str
    iteration_count: int
    combined_score: int
    ats_score: int
    recruiter_score: int
    top_keywords_matched: list[str]
    hard_gaps: list[str]
    latex_path: str
    score_report_path: str


class GenerationResult(BaseModel):
    resume_latex: str
    score_report: ScoreReport | None = None
    metadata: ResumeMetadata
    claim_ledger: list[EvidenceClaim] = Field(default_factory=list)


# ── Learning / optimize ────────────────────────────────────────────────────

class LearningUpdate(BaseModel):
    ats_lessons_appended: list[str]
    recruiter_lessons_appended: list[str]
    successful_patterns_appended: list[str]
    weak_patterns_appended: list[str]
    summary: str


class OptimizationResult(BaseModel):
    learning_update: LearningUpdate
    revised_ats_score: ATSScore
    revised_recruiter_score: RecruiterScore
    recommendations: list[str]
