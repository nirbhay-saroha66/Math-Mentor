from groq import Client
import os

client = Client(api_key=os.getenv("GROQ_API_KEY"))

def explain_solution(solution):
    prompt = f"""
    Based on this solution, provide a clear, step-by-step explanation that a student can easily follow.

    Solution: {solution}

    Instructions for your response:
    1. Break down the solution into numbered steps (Step 1, Step 2, etc.)
    2. Explain each mathematical concept using simple language
    3. Use LaTeX for mathematical expressions where needed (wrap in $ for inline, $$ for display)
    4. Show intermediate calculations clearly
    5. Make it educational and easy to follow
    6. IMPORTANT: Write clean, readable text without raw LaTeX code visible. 
    7. If you use any LaTeX, ensure it's properly formatted and displayable

    Format your response as clean Markdown that will render properly. 
    Do NOT include raw unprocessed LaTeX fragments.

    Provide the step-by-step explanation:
    """
    response = client.chat.completions.create(
        model="compound-beta",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content