# my_django_app/recc_engine.py
import os
import re
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Initialize the model once when the server starts
model = SentenceTransformer("all-MiniLM-L6-v2")

SKILLS = [
    "Python","Java","C++","C#","JavaScript","TypeScript","SQL",
    "Django","Flask","FastAPI","Spring Boot",".NET",
    "React","Angular","Vue","Docker","Kubernetes",
    "AWS",  "Azure",  "GCP", "MySQL","PostgreSQL",
    "MongoDB","Redis", "Git","Linux","TensorFlow","PyTorch","Pandas","NumPy",
    "Scikit-learn","REST API","GraphQL","CI/CD","Jenkins",
    "Kafka","Spark","Programming", "Software Logic", "Software Troubleshooting"
]

def extract_skills(text, skill_list=SKILLS):
    found = []
    text = text.lower()
    for skill in skill_list:
        if re.search(r"\b" + re.escape(skill.lower()) + r"\b", text):
            found.append(skill)
    return sorted(found)

def normalize_resume(resume):
    profile = {}
    profile["skills"] = list(set(
        resume.get("technical_skills", []) +
        resume.get("tools", []) +
        resume.get("frameworks", []) +
        resume.get("databases", []) +
        resume.get("cloud_skills", []) +
        resume.get("project_skills", [])
    ))
    profile["soft_skills"] = resume.get("soft_skills", [])
    profile["education"] = resume.get("degrees", [])
    profile["experience"] = resume.get("total_experience_years", 0)
    profile["job_titles"] = resume.get("job_titles", [])                                                                                                                                  
    return profile

def generate_query(profile):
    if profile["job_titles"]:
        return profile["job_titles"][0]
    return "Software Engineer"

def search_jobs(query):
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=20&what={query}"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    return response.json().get("results", [])


def normalize_jobs(jobs):
    normalized = []
    for job in jobs:
        description = " ".join(job.get("description", "").split()[:200])
        skills = extract_skills(description)
        normalized.append({
            "title": job.get("title", ""),
            "company": job.get("company", {}).get("display_name", ""),
            "location": job.get("location", {}).get("display_name", ""),
            "salary_min": job.get("salary_min", ""),
            "salary_max": job.get("salary_max", ""),
            "contract_time": job.get("contract_time", ""),
            "contract_type": job.get("contract_type", ""),
            "redirect_url": job.get("redirect_url","#"),
            "category": job.get("category", {}).get("label", ""),
            "description": description,
            "skills": skills
        })
    return normalized

def create_resume_text(profile):
    return f"""
    Previous Job Titles: {' '.join(profile['job_titles'])}\n
    Skills: {' '.join(profile['skills'])}\n
    Soft Skills: {' '.join(profile['soft_skills'])}\n
    Education: {' '.join(profile['education'])}\n
    Experience: {profile['experience']} Years
    """

def create_job_text(job):
    return f"""
    Job Title: {job['title']}\n
    Company: {job['company']}\n
    Location: {job['location']}\n
    Salary: {job['salary_min']} - {job['salary_max']}\n
    Required Skills: {','.join(job['skills'])}
    """

def get_recommendations(resume_data):
    #The main orchestration function
    profile = normalize_resume(resume_data)
    query = generate_query(profile)
    raw_jobs = search_jobs(query)
    cleaned_jobs = normalize_jobs(raw_jobs)

    if not cleaned_jobs:
        return[]

    #resume encode
    resume_text = create_resume_text(profile)
    resume_embedding = model.encode(resume_text)
    
    # Skill mapping
    skill_map = {s.lower(): s for s in SKILLS}
    resume_skills = set(map(str.lower, profile["skills"]))
    
    #encode all jobs
    job_text = [create_job_text(job) for job in cleaned_jobs]
    job_embedding = model.encode(job_text)

    recommendations = []
    for i,job in enumerate(cleaned_jobs):  
        score = cosine_similarity([resume_embedding], [job_embedding[i]])[0][0]
        job_skills = set(map(str.lower, job["skills"]))    
        matched_skill = [skill_map[s] for s in (job_skills & resume_skills) if s in skill_map]
        missing_skill = [skill_map[s] for s in (job_skills - resume_skills) if s in skill_map]
        
        recommendations.append({
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "match_percentage": round(float(score) * 100, 2),
            "Matched_Skills": ", ".join(matched_skill),
            "Missing_Skills": ", ".join(missing_skill),
            "redirect_url": job.get("redirect_url", "#"),
        })
        
    return sorted(recommendations, key=lambda x: x["match_percentage"], reverse=True)[:10]