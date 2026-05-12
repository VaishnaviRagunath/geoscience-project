from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np

client = MongoClient("mongodb://localhost:27017/")
db = client["geoscience_db"]

clean_collection = db["cleaned_geoscience_data"]
embedding_collection = db["geoscience_embeddings"]

# Clear old (already empty, but safe)
embedding_collection.delete_many({})
print("Starting fresh embeddings...")

model = SentenceTransformer("all-MiniLM-L6-v2")

for doc in clean_collection.find():

    text = doc.get("content", "")
    url = doc.get("source_url", "")

    # 🔥 SIMPLE CHUNKING
    chunks = [text[i:i+400] for i in range(0, len(text), 400)]

    for chunk in chunks:
        if len(chunk.strip()) < 100:
            continue

        embedding = model.encode(chunk)
        embedding = embedding / np.linalg.norm(embedding)   # 🔥 normalize
        embedding = embedding.tolist()

        embedding_collection.insert_one({
            "prompt": "",
            "answer": chunk,
            "embedding": embedding,
            "source_url": url
        })

    print("Processed one document")

print("✅ Embeddings rebuilt correctly")

# 🔥 ADD CORE DEFINITIONS
definitions = [
    "Lithosphere is the rigid outer layer of the Earth consisting of the crust and upper mantle.",
    "Biosphere is the global sum of all ecosystems representing the zone of life on Earth.",
    "Hydrosphere includes all water bodies on Earth such as oceans rivers and lakes.",
    "Atmosphere is the layer of gases surrounding Earth.",
    "Magma is molten rock beneath Earth's surface.",
    "Lava is molten rock that reaches Earth's surface."
]

for text in definitions:
    embedding = model.encode(chunk)
    embedding = embedding / np.linalg.norm(embedding)   # 🔥 normalize
    embedding = embedding.tolist()
    embedding_collection.insert_one({
        "prompt": "",
        "answer": text,
        "embedding": embedding,
        "source_url": "manual"
    })