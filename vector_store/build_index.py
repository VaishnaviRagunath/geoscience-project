from pymongo import MongoClient
import numpy as np
import faiss
import pickle

print("Connecting to MongoDB...")

client = MongoClient("mongodb://localhost:27017/")
db = client["geoscience_db"]

collection = db["geoscience_embeddings"]

documents = list(collection.find())

print("Total embeddings:", len(documents))

vectors = []
metadata = []

for doc in documents:
    embedding = doc["embedding"]

    vectors.append(embedding)

    metadata.append({
        "prompt": doc["prompt"],
        "answer": doc["answer"],
        "source_url": doc["source_url"]
    })

vectors = np.array(vectors).astype("float32")

dimension = vectors.shape[1]

print("Vector dimension:", dimension)

print("Building FAISS index...")

index = faiss.IndexFlatL2(dimension)

index.add(vectors)

print("Total vectors in index:", index.ntotal)

faiss.write_index(index, "geoscience_index.faiss")

with open("metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

print("FAISS index created successfully")