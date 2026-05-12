from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["geoscience_db"]

collection = db["structured_geoscience_data"]

documents = collection.find()

updated = 0

for doc in documents:

    prompt = doc.get("prompt", "").strip()
    answer = doc.get("answer", "").strip()

    # Fix bad prompts
    if prompt == "" or prompt == "What is ?" or len(prompt) < 8:

        # generate new prompt from answer
        first_sentence = answer.split(".")[0]

        new_prompt = f"What is {first_sentence[:40]}?"

        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"prompt": new_prompt}}
        )

        updated += 1

print("Prompts fixed:", updated)