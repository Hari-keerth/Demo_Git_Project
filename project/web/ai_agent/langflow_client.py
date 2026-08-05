import json
import requests

LANGFLOW_URL = "http://localhost:7860/api/v1/run/153927c3-a67d-4e19-bd9d-8921132aa9de"


def run_langflow(state):

    payload = {
        "input_value": {
            "resume_analysis": state.resume_text,
            "job_description": state.job_description,
            "recruiter_email": state.recruiter_email,
        }
    }

    response = requests.post(
        LANGFLOW_URL,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    try:
        output = (
            data["outputs"][0]
                ["outputs"][0]
                ["results"]["message"]["text"]
        )

        # If Langflow already returned a JSON string
        if isinstance(output, str):
            return json.loads(output)

        return output

    except Exception as e:
        raise Exception(
            f"Unable to parse Langflow response.\n\n"
            f"Response:\n{data}\n\n"
            f"Error: {e}"
        )