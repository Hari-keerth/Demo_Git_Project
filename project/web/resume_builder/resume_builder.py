from groq import Groq
import os
from dotenv import load_dotenv
from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# load_dotenv(BASE_DIR / ".env")

# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY")
# )

BASE_DIR = Path(__file__).resolve().parent.parent.parent

print("BASE_DIR:", BASE_DIR)

dotenv_loaded = load_dotenv(BASE_DIR / ".env")

print("Dotenv loaded:", dotenv_loaded)

api_key = os.getenv("GROQ_API_KEY")

print("API Key:", api_key[:12] + "..." if api_key else "None")

client = Groq(api_key=api_key)

def build_prompt(data):

    return f"""
You are an expert ATS Resume Writer.

Create a modern ATS-friendly resume.

STRICT RULES:

1. Return ONLY valid HTML.
2. Never return Markdown.
3. Never use ```html.
4. Never include <html>, <head>, or <body>.
5. Use ONLY the following CSS classes:

resume-header
resume-name
resume-contact
resume-section
resume-section-title
resume-item
resume-item-header
resume-item-subtitle
resume-list

Resume Type:
{data.get("resume_type", "")}

Personal Information:
{data.get("personal_info", "")}

Education:
{data.get("education", "")}

Experience:
{data.get("experience", "")}

Projects:
{data.get("projects", "")}

Skills:
{data.get("skills", "")}

Leadership / Extracurricular:
{data.get("extracurricular", "")}

Generate a professional ATS-friendly one-page resume.

Return ONLY HTML.
"""


def generate_resume(data):

    prompt = build_prompt(data)

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",
                    "content": "You are an ATS Resume Builder."
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.4,

            max_tokens=4096

        )

        html = response.choices[0].message.content

        html = (
            html
            .replace("```html", "")
            .replace("```", "")
            .strip()
        )

        return html

    except Exception as e:

        raise Exception(f"Groq Error: {str(e)}")