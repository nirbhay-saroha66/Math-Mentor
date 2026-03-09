from groq import Client
import os

client = Client(api_key=os.getenv("GROQ_API_KEY"))

def verify_solution(solution):
    prompt = f"""
    Verify the correctness of this solution:
    {solution}

    Is it correct? Provide confidence level.
    """
    response = client.chat.completions.create(
        model="compound-beta",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content