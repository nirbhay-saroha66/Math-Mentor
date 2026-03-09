import sqlite3
import json

def get_connection():
    return sqlite3.connect('memory.db', check_same_thread=False)

# Create table if not exists
conn = get_connection()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY,
    problem_text TEXT,
    parsed TEXT,
    context TEXT,
    solution TEXT,
    verification TEXT,
    feedback TEXT,
    comment TEXT
)''')
conn.commit()
conn.close()

def store_interaction(problem_text, parsed, context, solution, verification, feedback, comment=""):
    print(f"DEBUG: Storing interaction for problem: {problem_text[:50]}...")
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO interactions (problem_text, parsed, context, solution, verification, feedback, comment) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (problem_text, json.dumps(parsed), json.dumps(context), solution, verification, feedback, comment))
    conn.commit()
    conn.close()
    print("DEBUG: Interaction stored successfully.")

def retrieve_similar(query):
    print(f"DEBUG: Searching for similar to: {query[:60]}...")
    conn = get_connection()
    c = conn.cursor()
    
    # Get all interactions
    c.execute("SELECT * FROM interactions")
    all_interactions = c.fetchall()
    conn.close()
    
    print(f"DEBUG: Total interactions in DB: {len(all_interactions)}")
    
    if not all_interactions:
        print("DEBUG: No interactions found in database")
        return []
    
    # Improved similarity: check if first 40 chars match (ignoring exact text match)
    similar_results = []
    query_first_40 = query[:40].lower()
    
    for interaction in all_interactions:
        stored_text = interaction[1]  # problem_text is at index 1
        stored_first_40 = stored_text[:40].lower() if stored_text else ""
        
        print(f"DEBUG: Comparing '{query_first_40}' with '{stored_first_40}'")
        
        # Match if first 40 chars are similar (at least 80% match)
        if query_first_40 == stored_first_40 or similar_strings(query, stored_text):
            similar_results.append(interaction)
            print(f"DEBUG: MATCH FOUND!")
    
    print(f"DEBUG: Found {len(similar_results)} similar problems")
    return similar_results

def similar_strings(s1, s2, threshold=0.8):
    """Check if two strings are similar (at least threshold% match)"""
    from difflib import SequenceMatcher
    ratio = SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    print(f"DEBUG: Similarity ratio: {ratio:.2f}")
    return ratio >= threshold