from groq import Groq
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MEDICAL_PROMPT = """
You are a medical report simplifier. Your job is to help 
patients understand their medical reports in plain simple English.

Analyze the medical report and return a JSON response with 
exactly this structure:
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

Return ONLY the JSON. No extra text. No markdown. No backticks.
"""


def simplify_text_report(text: str) -> dict:
    """Send text report to Groq for simplification"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": MEDICAL_PROMPT},
                {"role": "user", "content": f"Medical Report:\n{text}"},
            ],
            temperature=0.1,
            max_tokens=2000,
        )

        result_text = response.choices[0].message.content.strip()

        # Clean any markdown formatting
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]

        return json.loads(result_text.strip())

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return {
            "simplified_text": "Report analyzed but formatting issue occurred.",
            "risk_level": "Unknown",
            "abnormal_values": [],
            "action_plan": "Please consult your doctor.",
            "disclaimer": "AI-assisted summary. Always consult your doctor.",
        }
    except Exception as e:
        print(f"Groq text error: {e}")
        return {
            "simplified_text": "Unable to analyze report. Please try again.",
            "risk_level": "Unknown",
            "abnormal_values": [],
            "action_plan": "Please consult your doctor.",
            "disclaimer": "AI-assisted summary. Always consult your doctor.",
        }


def simplify_image_report(image_bytes: bytes, media_type: str = "image/png") -> dict:
    """
    Send image/X-ray to Groq Vision for analysis.
    Uses llama-4-scout which supports vision.
    """
    try:
        image_data = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": MEDICAL_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            },
                        },
                    ],
                }
            ],
            temperature=0.1,
            max_tokens=2000,
        )

        result_text = response.choices[0].message.content.strip()

        # Clean any markdown formatting
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]

        return json.loads(result_text.strip())

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return {
            "simplified_text": "Image analyzed but formatting issue occurred.",
            "risk_level": "Unknown",
            "abnormal_values": [],
            "action_plan": "Please consult your doctor.",
            "disclaimer": "AI-assisted summary. Always consult your doctor.",
        }
    except Exception as e:
        print(f"Groq image error: {e}")
        return {
            "simplified_text": "Unable to analyze image. Please try again.",
            "risk_level": "Unknown",
            "abnormal_values": [],
            "action_plan": "Please consult your doctor.",
            "disclaimer": "AI-assisted summary. Always consult your doctor.",
        }
