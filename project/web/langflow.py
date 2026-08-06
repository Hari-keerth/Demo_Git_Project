import json
import uuid
import requests

LANGFLOW_URL = "http://127.0.0.1:7860"
FLOW_ID = "7f17ac32-ca71-4eae-8279-f59187dd6d19"
API_KEY = "sk-4vGgmANvnvqbtIExw3QI-K9spk5UKlluujhyXry2uwg"


def analyze_resume(resume_text, job_description):

    combined_input = f"""
=========================
RESUME
=========================

{resume_text}

=========================
JOB DESCRIPTION
=========================

{job_description}
"""

    payload = {
        "input_value": combined_input,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": str(uuid.uuid4())
    }

    headers = {
        "x-api-key": API_KEY
    }

    response = requests.post(
        f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}",
        json=payload,
        headers=headers,
        timeout=180
    )

    response.raise_for_status()

    data = response.json()

    ai_response = data["outputs"][0]["outputs"][0]["results"]["message"]["text"]

    return json.loads(ai_response)


#---------------------------------------------------------------------------------------------------
#sk-4vGgmANvnvqbtIExw3QI-K9spk5UKlluujhyXry2uwg
#---------------------------------------------------------------------------------------------------