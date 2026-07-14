import os
import json
import re

from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

print("Loaded Groq Key:", api_key[:10] if api_key else "NO KEY FOUND")


client = Groq(
    api_key=api_key
)

MODEL = "llama-3.3-70b-versatile"
# -------------------------------------------------------
# Helper
# -------------------------------------------------------

def _extract_json(text):

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        return json.loads(match.group())

    raise Exception("Groq did not return valid JSON")


# -------------------------------------------------------
# Resume Parser
# -------------------------------------------------------

def parse_resume(resume_text):

    prompt = f"""
You are an ATS Resume Parser.

Extract the following information.

Return ONLY valid JSON.

{{
    "name":"",
    "email":"",
    "phone":"",
    "education":[],
    "technical_skills":[],
    "soft_skills":[],
    "tools":[],
    "frameworks":[],
    "databases":[],
    "projects":[],
    "experience":[],
    "certifications":[]
}}

Resume:

{resume_text}
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0

    )

    result = response.choices[0].message.content

    return _extract_json(result)


# -------------------------------------------------------
# Job Description Parser
# -------------------------------------------------------

def parse_job_description(job_description):

    prompt = f"""
You are an ATS Job Description Parser.

Return ONLY valid JSON.

{{
    "job_title":"",
    "company":"",
    "required_skills":[],
    "preferred_skills":[],
    "tools":[],
    "frameworks":[],
    "databases":[],
    "experience_required":"",
    "education_required":"",
    "responsibilities":[]
}}

Job Description:

{job_description}
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0

    )

    result = response.choices[0].message.content

    return _extract_json(result)