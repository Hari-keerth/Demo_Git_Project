from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_ats(resume_json, jd_json):

    resume_skills = set(
        skill.lower()
        for skill in resume_json.get("technical_skills", [])
    )

    jd_skills = set(
        skill.lower()
        for skill in jd_json.get("required_skills", [])
    )

    matched = list(resume_skills & jd_skills)
    missing = list(jd_skills - resume_skills)

    if len(jd_skills) == 0:
        keyword_score = 0
    else:
        keyword_score = (len(matched) / len(jd_skills)) * 100

    resume_text = " ".join(resume_skills)
    jd_text = " ".join(jd_skills)

    emb1 = model.encode([resume_text])
    emb2 = model.encode([jd_text])

    semantic_score = cosine_similarity(emb1, emb2)[0][0] * 100

    ats_score = round(
        (keyword_score * 0.6) +
        (semantic_score * 0.4),
        2
    )

    strengths = []

    if keyword_score > 70:
        strengths.append("Strong skill match")

    if semantic_score > 70:
        strengths.append("Good semantic relevance")

    improvements = []

    if missing:
        improvements.append("Learn missing technical skills")

    if keyword_score < 60:
        improvements.append("Increase keyword coverage")

    return {

        "ats_score": ats_score,

        "matched_skills": matched,

        "missing_skills": missing,

        "recommended_skills": missing,

        "strengths": strengths,

        "improvements": improvements

    }