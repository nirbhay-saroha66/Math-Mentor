from groq import Client
import os

client = Client(api_key=os.getenv("GROQ_API_KEY"))

def solve_problem(parsed, context):
    prompt = f"""
    Solve the following math problem completely. Show all work clearly and provide ONLY ONE final answer in LaTeX boxed format at the end.

    Problem: {parsed['problem_text']}

    Context from knowledge base: {context}

    Instructions:
    1. Show all work and steps clearly with proper mathematical notation
    2. Use LaTeX for mathematical expressions where appropriate
    3. At the very end, provide the final answer in this exact format: \\boxed{{final_answer}}
    4. The boxed answer should contain ONLY the final result (no extra text or explanations)
    5. For fractions, use \\frac{{numerator}}{{denominator}} format
    6. Do not use \\boxed{{}} anywhere else in the solution

    Example of correct final answer format:
    \\boxed{{\\frac{{7}}{{13}}}}

    Provide a complete solution with one boxed final answer:
    """
    response = client.chat.completions.create(
        model="compound-beta",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content