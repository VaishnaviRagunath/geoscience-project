import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from mistralai.client import MistralClient
from sqlalchemy import text
from dotenv import load_dotenv
import os

# 🔥 Load environment variables
load_dotenv()

# 🔥 Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔥 Load FAISS index once
print("Loading FAISS index...")
index = faiss.read_index("vector_store/geoscience_index.faiss")

# 🔥 Load metadata
with open("vector_store/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

print("Index loaded successfully")

# 🔥 Mistral API
api_key = os.getenv("MISTRAL_API_KEY")
client = MistralClient(api_key=api_key)

# 🔥 Cache
query_cache = {}

def retrieve_context(query, k=5):
      
    improved_query = "Explain clearly in geoscience terms: " + query

    if improved_query in query_cache:
        query_embedding = query_cache[improved_query]
    else:
        query_embedding = embedding_model.encode([improved_query]).astype("float32")
        faiss.normalize_L2(query_embedding)   # 🔥 important
        query_cache[improved_query] = query_embedding

    distances, indices = index.search(query_embedding, k)

    results = []
    sources = []

    for i in indices[0]:
        text = metadata[i].get("answer", "")

        # 🔥 keep only basic filtering
        if len(text.strip()) < 100:
            continue
        if "data identifying" in text.lower():
            continue
        if "scale" in text.lower():
            continue

        results.append(text[:300])
        sources.append(metadata[i].get("source_url", ""))

    # fallback
    if not results:
        for i in indices[0]:
            text = metadata[i].get("answer", "")
            results.append(text[:300])
            sources.append(metadata[i].get("source_url", ""))

    context = "\n\n".join(results)

    return context, sources


# 🤖 Ask Mistral (stable + improved)
def ask_mistral(question, context):
      
    prompt = f"""
You are a helpful geoscience expert.

Give a clear and moderately detailed explanation.

Instructions:
- Explain simply
- Include key points
- Use bullet points if useful
- Keep answer informative but not too long

Context:
{context}

Question:
{question}

Answer:
"""

    try:
        response = client.chat(
            model="mistral-medium",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("❌ Mistral Error:", e)
        return "Error generating response. Check API or internet."


# CLI (optional)
def run_assistant():
    print("\n🌍 Geoscience AI Research Assistant")
    print("-----------------------------------")

    while True:
        question = input("\nAsk a question (type 'exit' to quit): ")

        if question.lower() == "exit":
            break

        context, sources = retrieve_context(question)
        answer = ask_mistral(question, context)

        print("\nAnswer:\n", answer)
        print("\nSources:")
        for src in sources:
            print(src)