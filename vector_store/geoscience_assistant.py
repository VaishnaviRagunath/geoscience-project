import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from mistralai.client import MistralClient

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
api_key = "vzkzUFJL9VoAS13Agc0SzUgJ4tETu9Dn"  # ⚠️ replace this
client = MistralClient(api_key=api_key)

# 🔥 Cache
query_cache = {}

# 🔍 Retrieve context
def retrieve_context(query, k=3):

    if query in query_cache:
        query_embedding = query_cache[query]
    else:
        query_embedding = embedding_model.encode([query]).astype("float32")
        query_cache[query] = query_embedding

    distances, indices = index.search(query_embedding, k)

    results = []
    sources = []

    for i in indices[0]:
        text = metadata[i]["answer"][:400]  # balanced
        results.append(text)
        sources.append(metadata[i]["source_url"])

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