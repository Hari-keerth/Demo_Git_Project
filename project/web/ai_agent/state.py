from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class AgentState:
    """
    Shared state across the entire AI Agent workflow.
    """

    # -------------------------
    # Input
    # -------------------------

    resume_path: Path
    resume_text: str
    job_description: str
    recruiter_email: str = ""

    # -------------------------
    # Resume Analysis
    # -------------------------

    parsed_resume: Dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Job Analysis
    # -------------------------

    job_analysis: Dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Skill Matching
    # -------------------------

    skill_match: Dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Strategy
    # -------------------------

    strategy: Dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Company Research
    # -------------------------

    company_research: Dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Generated Content
    # -------------------------

    email_subject: str = ""
    email_body: str = ""
    cover_letter: str = ""

    # -------------------------
    # Evaluation
    # -------------------------

    quality_score: int = 0

    feedback: List[str] = field(default_factory=list)

    # -------------------------
    # Metadata
    # -------------------------

    logs: List[str] = field(default_factory=list)

    current_step: str = ""

    success: bool = False

    error: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)

    # -------------------------
    # Helper Methods
    # -------------------------

    def log(self, message: str):
        self.logs.append(message)

    def set_step(self, step: str):
        self.current_step = step
        self.logs.append(step)

    def fail(self, message: str):
        self.success = False
        self.error = message
        self.logs.append(f"ERROR: {message}")

    def complete(self):
        self.success = True