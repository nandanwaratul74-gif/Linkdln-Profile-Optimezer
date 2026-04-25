"""
llm.py — Centralized helper to call Google Gemini via the google-genai SDK.
"""

import json
import re

import google.generativeai as genai


def call_gemini(prompt: str, api_key: str, temperature: float = 0.7) -> str:
    """
    Call Gemini 2.5 Flash and return the raw text response.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
        ),
    )
    response = model.generate_content(prompt)
    return response.text


def call_gemini_json(prompt: str, api_key: str, temperature: float = 0.4) -> dict:
    """
    Call Gemini and parse the response as JSON.
    Strips markdown code fences if present.
    """
    raw = call_gemini(prompt, api_key, temperature)
    # Strip ```json ... ``` fences
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Attempt to extract the first JSON object/array
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise ValueError(f"Could not parse Gemini response as JSON:\n{raw}")
