import http.client
from dotenv import load_dotenv
import os
import json
from urllib.parse import quote

load_dotenv()

API_KEY = os.getenv("Job_Key")

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "jsearch.p.rapidapi.com",
    "Content-Type": "application/json"
}

def get_jobs(skills):

    query = quote(" ".join(skills))

    conn = http.client.HTTPSConnection(
        "jsearch.p.rapidapi.com"
    )

    endpoint = (
        f"/search-v2?"
        f"query={query}"
        f"&num_pages=1"
        f"&country=us"
        f"&date_posted=all"
    )

    conn.request(
        "GET",
        endpoint,
        headers=headers
    )

    res = conn.getresponse()
    data = res.read()

    result = json.loads(
        data.decode("utf-8")
    )

    jobs = []

    if "data" not in result:

        print("RapidAPI Error:")
        print(result)

        return []

    for job in result["data"].get("jobs", [])[:5]:

        jobs.append({
            "title": job.get("job_title"),
            "company": job.get("employer_name"),
            "location": job.get("job_location"),
            "apply_link": job.get("job_apply_link")
        })

    return jobs