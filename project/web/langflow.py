# # import requests

# # LANGFLOW_URL = "http://localhost:7860/api/v1/run/472e1392-4d71-4175-8ba5-ef833f0e9eae"

# # API_KEY = "sk-wIdfifYqCx0HjemCzssbYHub5k5LZ27v3_LAvBnKXA0"


# # def generate_question(role, difficulty, asked_questions):

# #     payload = {
# #         "input_value": "",
# #         "input_type": "chat",
# #         "output_type": "chat",
# #         "tweaks": {
# #             "PromptTemplate-YOUR_ID": {
# #                 "role": role,
# #                 "difficulty": difficulty,
# #                 "asked_questions": "\n".join(asked_questions)
# #             }
# #         }
# #     }

# #     response = requests.post(
# #         LANGFLOW_URL,
# #         json=payload,
# #         headers={
# #             "Content-Type": "application/json",
# #             "x-api-key": API_KEY
# #         }
# #     )

# #     response.raise_for_status()

# #     data = response.json()

# #     print(data)

# #     question = data["outputs"][0]["outputs"][0]["results"]["text"]["text"]

# #     return question

# import requests

# LANGFLOW_URL = "http://localhost:7860/api/v1/run/472e1392-4d71-4175-8ba5-ef833f0e9eae"

# LANGFLOW_API_KEY = "sk-wIdfifYqCx0HjemCzssbYHub5k5LZ27v3_LAvBnKXA0"

# QUESTION_COMPONENT_ID = "PromptTemplate-QUESTION_ID"
# EVALUATION_COMPONENT_ID = "Prompt Template-KzWTR"


# def _post_to_langflow(payload: dict):
#     response = requests.post(
#         LANGFLOW_URL,
#         headers={
#             "Content-Type": "application/json",
#             "x-api-key": LANGFLOW_API_KEY,
#         },
#         json=payload,
#         timeout=60,
#     )
#     response.raise_for_status()
#     return response.json()


# def _extract_text(result: dict) -> str:
#     return result["outputs"][0]["outputs"][0]["results"]["text"]["text"]


# def generate_question(role, difficulty, asked_questions):

#     payload = {
#         "input_value": "",
#         "input_type": "chat",
#         "output_type": "chat",
#         "tweaks": {
#             QUESTION_COMPONENT_ID: {
#                 "role": role,
#                 "difficulty": difficulty,
#                 "asked_questions": "\n".join(asked_questions)
#             }
#         }
#     }

#     result = _post_to_langflow(payload)
#     return _extract_text(result)


# def evaluate_interview(role, interview_data):

#     payload = {
#         "input_value": "",
#         "input_type": "chat",
#         "output_type": "chat",
#         "tweaks": {
#             EVALUATION_COMPONENT_ID: {
#                 "role": role,
#                 "interview_data": interview_data
#             }
#         }
#     }

#     result = _post_to_langflow(payload)
#     return _extract_text(result)


# _____________________________________


import requests

# ============================
# Langflow Configuration
# ============================

QUESTION_FLOW_URL = (
    "http://localhost:7860/api/v1/run/472e1392-4d71-4175-8ba5-ef833f0e9eae"

)

EVALUATION_FLOW_URL = (
    "http://localhost:7860/api/v1/run/74e5a1a4-4c5c-4e74-af3d-b25075014bb3"

)

LANGFLOW_API_KEY = "sk-wIdfifYqCx0HjemCzssbYHub5k5LZ27v3_LAvBnKXA0"

QUESTION_COMPONENT_ID = "Prompt Template-nBVfF"
EVALUATION_COMPONENT_ID = "Prompt Template-KzWTR"


# ============================
# Common Function
# ============================

def _post_to_langflow(url, payload):

    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "x-api-key": LANGFLOW_API_KEY,
        },
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    print("=" * 80)
    print(data)
    print("=" * 80)

    return data


def _extract_text(result):

    return (
        result["outputs"][0]
              ["outputs"][0]
              ["results"]
              ["message"]
              ["text"]
    )


# ============================
# Question Generator
# ============================

def generate_question(role, difficulty, asked_questions):

    clean_questions = [
        str(q)
        for q in asked_questions
        if q is not None
    ]

    payload = {
        "input_value": "",
        "input_type": "chat",
        "output_type": "chat",
        "tweaks": {
            QUESTION_COMPONENT_ID: {
                "role": role,
                "difficulty": difficulty,
                "asked_questions": "\n".join(clean_questions)
            }
        }
    }

    result = _post_to_langflow(
        QUESTION_FLOW_URL,
        payload
    )

    return _extract_text(result)


# ============================
# Interview Evaluation
# ============================

def evaluate_interview(role, interview_data):

    payload = {
        "input_value": "",
        "input_type": "chat",
        "output_type": "chat",
        "tweaks": {
            EVALUATION_COMPONENT_ID: {
                "role": role,
                "interview_data": interview_data
            }
        }
    }

    result = _post_to_langflow(
        EVALUATION_FLOW_URL,
        payload
    )

    return _extract_text(result)