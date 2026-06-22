import anthropic
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MEDICAL_PROMPT = """
You are a medical report simplifier. Your job is to help patients 
understand their medical reports in plain, simple English.

Analyze the medical report and return a JSON response with exactly 
this structure:
{
    "simplified_text": "Plain English explanation of the report",
    "risk_level": "High/Medium/Low",
    "abnormal_values": [
        {
            "name": "Test name",
            "value": "Patient value",
            "normal_range": "Normal range",
            "explanation": "What this means"
        }
    ],
    "action_plan": "Clear steps the patient should take",
    "disclaimer": "This is an AI-assisted summary for educational purposes only. Always consult your doctor."
}

Return ONLY the JSON. No extra text.
"""


def simplify_text_report(text: str) -> dict:
    """Send text report to Claude for simplification"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[
            {"role": "user", "content": f"{MEDICAL_PROMPT}\n\nMedical Report:\n{text}"}
        ],
    )

    result = response.content[0].text
    return json.loads(result)


def simplify_image_report(image_bytes: bytes, media_type: str = "image/png") -> dict:
    """Send image/X-ray to Claude Vision for analysis"""
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": MEDICAL_PROMPT},
                ],
            }
        ],
    )

    result = response.content[0].text
    return json.loads(result)
