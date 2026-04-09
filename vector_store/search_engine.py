import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

print("Loading FAISS index...")

# Load FAISS index
index = faiss.read_index("geoscience_index.faiss")

# Load metadata
with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

print("Index loaded successfully")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def search(question, k=3):

    print("\nGenerating embedding for query...")

    # Convert question to embedding
    query_embedding = model.encode(question)

    query_vector = np.array([query_embedding]).astype("float32")

    print("Searching FAISS index...")

    # Search FAISS
    distances, indices = index.search(query_vector, k)

    results = []

    for i in indices[0]:

        if i < len(metadata):
            results.append(metadata[i])

    return results


if __name__ == "__main__":

    while True:

        question = input("\nAsk a geoscience question (type 'exit' to quit): ")

        if question.lower() == "exit":
            break

        results = search(question)

        print("\nTop Results:\n")

        for r in results:

            print("Question:", r["prompt"])
            print("Answer:", r["answer"])
            print("Source:", r["source_url"])
            print("-" * 60)