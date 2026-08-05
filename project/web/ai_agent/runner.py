from pathlib import Path

from .state import AgentState
from .pdf_service import PDFService
from .langflow_client import run_langflow


def run_agent(
    resume_path: Path,
    job_description: str,
    recruiter_email: str = "",
):
    """
    Entry point for the AI Agent.

    Workflow:
        1. Extract resume text
        2. Create the agent state
        3. Send data to Langflow
        4. Return the parsed JSON response
    """

    # -----------------------------------------
    # Extract Resume Text
    # -----------------------------------------

    pdf_service = PDFService()

    resume_text = pdf_service.extract_text(resume_path)

    # -----------------------------------------
    # Build Agent State
    # -----------------------------------------

    state = AgentState(
        resume_path=resume_path,
        resume_text=resume_text,
        job_description=job_description,
        recruiter_email=recruiter_email,
    )

    # -----------------------------------------
    # Execute Langflow
    # -----------------------------------------

    result = run_langflow(state)

    # -----------------------------------------
    # Return Final JSON
    # -----------------------------------------

    return {
        "email_subject": result.get("email_subject", ""),
        "email_body": result.get("email_body", ""),
        "cover_letter": result.get("cover_letter", ""),

        "quality_score": result.get("quality_score", 0),
        "ats_match": result.get("ats_match", 0),

        "reflection_count": result.get("reflection_count", 0),
        "decision": result.get("decision", "KEEP"),

        "matched_skills": result.get("matched_skills", []),
        "missing_skills": result.get("missing_skills", []),

        "company_summary": result.get("company_summary", ""),
        "strategy": result.get("strategy", ""),

        "strengths": result.get("strengths", []),
        "weaknesses": result.get("weaknesses", []),
        "suggestions": result.get("suggestions", []),
    }