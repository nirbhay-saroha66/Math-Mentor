import re
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import os
from utils.ocr import extract_text_from_image
from utils.asr import transcribe_audio
from agents.parser_agent import parse_problem
from agents.intent_router_agent import route_intent
from agents.solver_agent import solve_problem
from agents.verifier_agent import verify_solution
from agents.explainer_agent import explain_solution
from memory.memory_manager import store_interaction, retrieve_similar
from rag.knowledge_base import retrieve_context


def clean_latex_for_streamlit(text):
    """Clean LaTeX for better Streamlit rendering"""
    if not text:
        return text

    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{aligned\}(.*?)\\end\{aligned\}', r'$$\n\1\n$$', text, flags=re.DOTALL)

    text = re.sub(r'\\[\d]+pt', '', text)
    text = re.sub(r'\\\s*quad\s*', ' ', text)
    text = re.sub(r'\\\s*qquad\s*', '  ', text)
    text = re.sub(r'\\\s*,\s*', '', text)
    text = re.sub(r'\\\s*;\s*', '', text)
    text = re.sub(r'\\\s*:\s*', '', text)
    text = re.sub(r'\\\s*!\s*', '', text)

    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\mathbf\{([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\\mathit\{([^}]+)\}', r'*\1*', text)

    text = re.sub(r'\$\$+', '$$', text)

    # FIX alignment artifacts
    text = text.replace("&=", "=")
    text = text.replace("&", "")

    return text

st.title("Math Mentor")

# Initialize session state
if 'problem_text' not in st.session_state:
    st.session_state.problem_text = ""
if 'parsed' not in st.session_state:
    st.session_state.parsed = {}
if 'context' not in st.session_state:
    st.session_state.context = []
if 'solution' not in st.session_state:
    st.session_state.solution = ""
if 'verification' not in st.session_state:
    st.session_state.verification = ""
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""
if 'similar' not in st.session_state:
    st.session_state.similar = []
if 'intent' not in st.session_state:
    st.session_state.intent = ""
if 'solved' not in st.session_state:
    st.session_state.solved = False

# NEW: agent trace
if 'trace' not in st.session_state:
    st.session_state.trace = []

# Input mode selector
input_mode = st.selectbox("Select Input Mode", ["Text", "Image", "Audio"])

problem_text = ""

if input_mode == "Text":
    problem_text = st.text_area("Enter your math problem:")

elif input_mode == "Image":
    uploaded_file = st.file_uploader("Upload an image of the math problem", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image")
        extracted_text = extract_text_from_image(uploaded_file)
        st.subheader("Extracted Text:")
        problem_text = st.text_area("Edit if necessary:", value=extracted_text)

elif input_mode == "Audio":
    uploaded_audio = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])
    if uploaded_audio:
        st.audio(uploaded_audio)
        transcript = transcribe_audio(uploaded_audio)
        st.subheader("Transcript:")
        problem_text = st.text_area("Edit if necessary:", value=transcript)

if st.button("Solve Problem"):

    # reset trace for new run
    st.session_state.trace = []

    if not problem_text.strip():
        st.error("Please provide a problem.")
        st.stop()

    # Parse
    parsed = parse_problem(problem_text)
    st.session_state.trace.append("Parser Agent → Parsed the problem structure")

    st.session_state.parsed = parsed
    st.session_state.problem_text = problem_text
    
    st.info("📍 **Input Processing**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Extracted Text", len(problem_text))
    with col2:
        st.metric("Topic Detected", parsed.get("topic", "unknown").upper())
    
    if parsed.get("raw_output") or parsed.get("parse_error"):
        st.warning("⚠️ Parser encountered issues:")
        st.code(parsed.get("raw_output", ""))
        if parsed.get("parse_error"):
            st.write(f"Error: {parsed['parse_error']}")

    if parsed.get('needs_clarification', False):
        st.warning("🔄 **HITL Triggered**: The problem needs clarification.")
        clarified_text = st.text_area("Edit the problem statement:", value=problem_text, key="clarify")
        if st.button("Re-parse"):
            parsed = parse_problem(clarified_text)
            st.session_state.parsed = parsed
            st.session_state.problem_text = clarified_text
        else:
            st.stop()

    # Route
    intent = route_intent(parsed)
    st.session_state.trace.append(f"Intent Router → Routed to {intent}")
    st.session_state.intent = intent

    # Retrieve context
    context = retrieve_context(parsed)
    st.session_state.trace.append("RAG Retriever → Retrieved knowledge base context")
    st.session_state.context = context

    # Memory
    similar = retrieve_similar(problem_text)
    st.session_state.trace.append("Memory Module → Retrieved similar past problems")
    st.session_state.similar = similar

    # Solve
    solution = solve_problem(parsed, context)
    st.session_state.trace.append("Solver Agent → Generated mathematical solution")
    st.session_state.solution = solution

    # Verify
    verification = verify_solution(solution)
    st.session_state.trace.append("Verifier Agent → Checked correctness")
    st.session_state.verification = verification

    if "not confident" in verification.lower() or "incorrect" in verification.lower():
        st.warning("🔄 **HITL Triggered**: Verifier is not confident. Please review and correct if needed.")
        corrected_solution = st.text_area("Corrected Solution:", value=solution, key="correct")
        if st.button("Use Corrected"):
            solution = corrected_solution
            st.session_state.solution = solution
            verification = "Manually corrected by user"
            st.session_state.verification = verification

    # Explain
    explanation = explain_solution(solution)
    st.session_state.trace.append("Explainer Agent → Generated step-by-step explanation")
    st.session_state.explanation = explanation

    explanation_clean = clean_latex_for_streamlit(explanation)

    st.session_state.solved = True


# Show results
if st.session_state.solved:

    parsed = st.session_state.parsed
    intent = st.session_state.intent
    context = st.session_state.context
    similar = st.session_state.similar
    solution = st.session_state.solution
    verification = st.session_state.verification
    explanation = st.session_state.explanation
    problem_text = st.session_state.problem_text
    
    explanation_clean = clean_latex_for_streamlit(explanation)

    st.success("✅ **Problem Solved**")
    
    boxed_matches = re.findall(r'\\boxed\{([^{}]*(?:\{[^}]*\}[^{}]*)*)\}', solution, re.DOTALL)
    if boxed_matches:
        final_answer = boxed_matches[-1]
        final_answer = re.sub(r'\s+', '', final_answer).strip()
        
        st.subheader("📌 Final Answer:")
        st.markdown(f"$$\\boxed{{{final_answer}}}$$")
    else:
        st.subheader("📌 Final Answer:")
        frac_pattern = re.findall(r'\\frac\{\d+\}\{\d+\}', solution)
        if frac_pattern:
            final_answer = frac_pattern[-1]
            st.markdown(f"$$\\boxed{{{final_answer}}}$$")
        else:
            st.info("Could not extract boxed answer. Check the raw solution below.")

    st.subheader("📚 Step-by-Step Explanation:")
    st.markdown(explanation_clean)

    st.divider()
    st.subheader("🔍 Agent Trace & Details")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Agent Trace","Parsed Problem", "RAG Context", "Solver Output", "Verification", "Memory"]
    )
    
    with tab1:
        st.write("### Agent Execution Trace")
        if st.session_state.trace:
            for i, step in enumerate(st.session_state.trace,1):
                st.write(f"{i}. {step}")
        else:
            st.info("No trace available.")

    with tab2:
        st.write("**Parser Agent Output:**")
        st.json(parsed)
        st.write(f"**Intent Router Result:** {intent}")
    
    with tab3:
        st.write("**Retrieved Context (RAG Pipeline):**")
        if context:
            for i, chunk in enumerate(context, 1):
                st.write(f"**Source {i}:** {chunk}")
        else:
            st.write("No context retrieved.")
    
    with tab4:
        st.write("**Solver Agent Output (Raw Solution):**")
        st.code(solution)
    
    with tab5:
        st.write("**Verifier Agent Result:**")
        st.info(verification)

    with tab6:
        st.write("**Memory & Learning (Similar Past Problems):**")
        if similar:
            st.success(f"Found {len(similar)} similar problem(s) in memory:")
            for i, sim in enumerate(similar[:5], 1):
                problem_mem = sim[1] if len(sim) > 1 else "N/A"
                feedback_mem = sim[6] if len(sim) > 6 else "N/A"
                st.write(f"**{i}. Problem:** {problem_mem[:100]}...")
                st.write(f"   **User Feedback:** {feedback_mem}")
        else:
            st.info("No similar problems in memory yet. This will be the first record.")

    st.divider()
    st.subheader("📋 Feedback & Learning")

    col1, col2 = st.columns([1,2])

    with col1:
        if st.button("✅ Correct"):
            store_interaction(problem_text, parsed, context, solution, verification, "correct")
            st.success("✅ Feedback recorded!")
            st.session_state.solved = False

    with col2:
        incorrect_comment = st.text_input("If incorrect, explain why:")
        if st.button("❌ Incorrect"):
            store_interaction(problem_text, parsed, context, solution, verification, "incorrect", incorrect_comment)
            st.success("❌ Feedback recorded.")
            st.session_state.solved = False