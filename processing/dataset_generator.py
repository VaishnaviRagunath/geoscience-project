from pymongo import MongoClient
import re
import random

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["geoscience_db"]

clean_collection = db["cleaned_geoscience_data"]
structured_collection = db["structured_geoscience_data"]


def generate_prompt(text):
    # Split text into sentences
    sentences = re.split(r'[.\n?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return "Explain this geoscience concept."

    first_sentence = sentences[0]

    # Extract topic (first few words)
    words = first_sentence.split()
    topic = " ".join(words[:4])  # first 4 words

    # Different question templates
    templates = [
        "What is {}?",
        "Explain {}.",
        "What are the causes of {}?",
        "Describe {} in geoscience.",
        "How does {} work?",
        "What is the significance of {} in Earth science?"
    ]

    template = random.choice(templates)

    return template.format(topic)


# Optional: Clear old structured data (recommended to avoid duplicates)
structured_collection.delete_many({})


for doc in clean_collection.find():

    content = doc.get("content", "").strip()

    if not content:
        continue

    prompt = generate_prompt(content)

    structured_doc = {
        "prompt": prompt,
        "answer": content,
        "source_url": doc.get("source_url", "")
    }

    structured_collection.insert_one(structured_doc)

    print("Dataset sample created")

print("Dataset generation completed")