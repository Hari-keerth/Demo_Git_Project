from web.AI_chatbot.user_profile import get_user_profile
from web.AI_chatbot.job_api import get_jobs
from web.AI_chatbot.groq_client import ask_groq
from web.models import ATSResult

def chatbot_response(question,request):

    latest_resume = (
        ATSResult.objects
        .filter(user=request.user)
        .order_by("-created_at")
        .first()
    )

    if latest_resume:

        user = latest_resume.resume_json

    else:

        user = {}

    skills = (
        user.get("technical_skills", []) +
        user.get("frameworks", []) +
        user.get("tools", []) +
        user.get("databases", []) +
        user.get("cloud_skills", [])
    )

    jobs = get_jobs(skills)

    conversation = request.session.get("conversation",[])

    system_prompt =f"""
You are an intelligent AI Job Assistant.

Your role is to help users with careers, jobs, resumes, interviews, skills, and professional development.

--------------------------------------------------
USER PROFILE
--------------------------------------------------
{user}

--------------------------------------------------
RECOMMENDED JOBS
--------------------------------------------------
{jobs}

--------------------------------------------------
INSTRUCTIONS
--------------------------------------------------

1. Always answer based on the user's profile whenever relevant.

2. Use the recommended jobs whenever the user asks about:
   - Jobs
   - Vacancies
   - Career opportunities
   - Suitable roles

3. If recommending jobs:
   - Mention the Job Title.
   - Mention the Company.
   - Mention the Location.
   - Include the Application Link.
   - Briefly explain why it matches the user's skills.

4. If the user asks about interviews:
   - Generate relevant interview questions.
   - Give sample answers when appropriate.
   - Share interview preparation tips.

5. If the user asks about skills:
   - Analyze the user's current skills.
   - Identify missing skills.
   - Suggest a learning roadmap.
   - Recommend projects to improve.

6. If the user asks about resumes:
   - Suggest improvements.
   - Identify missing sections.
   - Recommend stronger wording.

7. If the user asks for career advice:
   - Give practical and actionable guidance.
   - Base advice on the user's profile.

8. If the user asks something unrelated to careers, jobs, resumes, interviews, skills, or the user's profile:
   - Politely explain that you are an AI Job Assistant.
   - Do not answer unrelated questions.

--------------------------------------------------
RESPONSE FORMAT
--------------------------------------------------

Always format responses in Markdown.

Use:

# Main Heading

## Section Heading

- Bullet points

1. Numbered lists

**Bold** for important information.

Leave one blank line between sections.

When mentioning application links, include the full URL.

Keep the response concise, professional, and easy to read.
"""
    
    messages = [
        {
            "role":"system",
            "content": system_prompt
        }
    ]

    messages.extend(conversation)

    messages.append(
        {
            "role" : "user",
            "content" : question
        }
    )

    response = ask_groq(messages)

    conversation.append(

        {
            "role":"user",
            "content" : question
        }
    )

    conversation.append(
        {
            "role":"assistant",
            "content": response
        }
    )

    conversation = conversation[-10:]

    request.session['conversation']=conversation

  

    return response