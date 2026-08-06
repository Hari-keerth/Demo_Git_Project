import json
import requests
from django.conf import settings

LANGFLOW_URL = "http://127.0.0.1:7860"
FLOW_ID = "YOUR_FLOW_ID"
APPLICATION_TOKEN = "YOUR_APPLICATION_TOKEN"  # if your API requires one

import json
import requests


LANGFLOW_URL = "http://127.0.0.1:7860"

import json
import requests

LANGFLOW_URL = "http://127.0.0.1:7860"

FLOW_ID = "7f17ac32-ca71-4eae-8279-f59187dd6d19"


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

        "output_type": "chat"

    }

    response = requests.post(

        f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}",

        json=payload,

        timeout=180

    )

    response.raise_for_status()

    return response.json()