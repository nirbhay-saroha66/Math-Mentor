import chromadb
from sentence_transformers import SentenceTransformer
import streamlit as st
import os

# -----------------------------
# Load embedding model
# -----------------------------
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------
# Initialize vector DB
# -----------------------------
@st.cache_resource
def load_vector_db():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("math_kb")
    return collection


model = load_embedding_model()
collection = load_vector_db()


# -----------------------------
# Load knowledge base files
# -----------------------------
def load_knowledge_files():

    kb_path = "knowledge_base"
    docs = []

    for file in os.listdir(kb_path):
        if file.endswith(".md"):
            with open(os.path.join(kb_path, file), "r", encoding="utf-8") as f:
                docs.append(f.read())

    return docs


# -----------------------------
# Initialize knowledge base
# -----------------------------
def initialize_knowledge_base():

    if collection.count() == 0:

        docs = load_knowledge_files()

        embeddings = model.encode(docs)

        collection.add(
            documents=docs,
            embeddings=embeddings.tolist(),
            ids=[str(i) for i in range(len(docs))]
        )


initialize_knowledge_base()


# -----------------------------
# Retrieve context
# -----------------------------
def retrieve_context(parsed_problem, k=3):

    query = parsed_problem.get("problem_text", "")

    if not query:
        return []

    query_embedding = model.encode([query])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=k
    )

    if results["documents"]:
        return results["documents"][0]

    return []