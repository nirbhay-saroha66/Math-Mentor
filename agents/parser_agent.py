from groq import Client
import json
import os

import streamlit as st
client = Client(api_key=st.secrets["GROQ_API_KEY"])

def parse_problem(problem_text):
    prompt = f"""
    You are a parser that must output _only_ valid JSON. Do not include any explanations,
    markdown, or additional text. Produce a JSON object with the following keys:
    - problem_text: string (the original problem)
    - topic: one of "algebra", "probability", "calculus", "linear_algebra", or "unknown"
    - variables: list of variable names found
    - constraints: list of any constraints
    - needs_clarification: boolean

    Parse the math problem below and return the JSON object directly.

    Problem: {problem_text}
    """
    response = client.chat.completions.create(
        model="compound-beta",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    # Try to extract JSON from the response
    import re
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            parsed = json.loads(json_str)
            return parsed
        except json.JSONDecodeError:
            pass
    # Fallback
    parsed = {
        "problem_text": problem_text,
        "topic": "unknown",
        "variables": [],
        "constraints": [],
        "needs_clarification": False,
        "raw_output": text,
        "parse_error": "Could not extract valid JSON",
    }
    return parsed