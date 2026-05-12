from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to MongoDB...")
client = MongoClient("mongodb://localhost:27017/")
db = client["geoscience_db"]

input_collection = db["structured_geoscience_data"]
embedding_collection = db["geoscience_embeddings"]

total_docs = input_collection.count_documents({})
print("Total structured documents:", total_docs)

count = 0

for doc in input_collection.find():

    prompt = doc.get("prompt", "")
    answer = doc.get("answer", "")

    if not prompt or not answer:
        continue

    combined_text = prompt + " " + answer

    vector = model.encode(combined_text).tolist()

    embedding_doc = {
        "prompt": prompt,
        "answer": answer,
        "embedding": vector,
        "source_url": doc.get("source_url")
    }

    embedding_collection.insert_one(embedding_doc)

    count += 1
    print("Embedded:", count)

print("Embedding generation completed")