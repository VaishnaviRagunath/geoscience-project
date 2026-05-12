import requests
import time
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from vector_store.geoscience_assistant import retrieve_context

# Display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# 🔥 Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

API_URL = "http://127.0.0.1:8000/ask"

# 🔥 Test dataset (you can change later)
test_data = [
    {
        "question": "What is magma?",
        "ground_truth": "Magma is molten rock beneath Earth's surface."
    },
    {
        "question": "What is atmosphere?",
        "ground_truth": "Atmosphere is the layer of gases surrounding Earth."
    },
    {
        "question": "Explain tectonic plates",
        "ground_truth": "Tectonic plates are large pieces of Earth's lithosphere that move."
    }
]


# 🔹 Semantic Similarity
def semantic_similarity(a, b):
    emb1 = model.encode(a, convert_to_tensor=True)
    emb2 = model.encode(b, convert_to_tensor=True)
    return util.cos_sim(emb1, emb2).item()


# 🔹 Retrieval Accuracy (Improved)
def retrieval_accuracy(query, context, threshold=0.25):   # 🔥 LOWERED threshold

    if not context.strip():
        return 0

    docs = context.split("\n\n")

    query_emb = model.encode(query, convert_to_tensor=True)

    relevant = 0

    for doc in docs:
        if len(doc.strip()) < 30:
            continue

        doc_emb = model.encode(doc, convert_to_tensor=True)
        score = util.cos_sim(query_emb, doc_emb).item()

        print(f"   → Doc Score: {round(score, 3)}")  # 🔍 debug

        if score > threshold:
            relevant += 1

    return relevant / len(docs) if docs else 0


# 🔹 Call API
def get_answer(question):
    response = requests.post(API_URL, json={
        "user_id": "eval_user",
        "question": question
    })
    return response.json().get("answer", "")


# 🔹 Main Evaluation
def evaluate():
    results = []

    for item in test_data:
        question = item["question"]
        ground_truth = item["ground_truth"]

        print(f"\n🔍 Evaluating: {question}")

        # 🔹 Retrieval
        context, _ = retrieve_context(question)

        print("\n--- Retrieved Context ---")
        print(context[:500])
        print("------------------------")

        retrieval_acc = retrieval_accuracy(question, context)
        retrieval_similarity = semantic_similarity(question, context)

        # 🔹 LLM Answer
        start = time.time()
        answer = get_answer(question)
        end = time.time()

        response_time = end - start
        answer_similarity = semantic_similarity(answer, ground_truth)

        print("\n--- LLM Answer ---")
        print(answer[:300])
        print("------------------")

        results.append({
            "Question": question,
            "Retrieval Accuracy": round(retrieval_acc, 3),
            "Retrieval Similarity": round(retrieval_similarity, 3),
            "Answer Similarity": round(answer_similarity, 3),
            "Response Time (s)": round(response_time, 2)
        })

    df = pd.DataFrame(results)
    df.to_csv("evaluation_results.csv", index=False)

    print("\n✅ Evaluation Done!")
    print(df)


if __name__ == "__main__":
    evaluate()