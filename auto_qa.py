import random
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import csv
import datetime
from pymongo import MongoClient

# -------- CLEAN TEXT --------
def clean_text(text):
    text = text.replace("**", "")
    text = text.replace("*", "")
    return text.strip()

# -------- LOAD MODELS --------
model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index("geoscience_index.faiss")

with open("metadata.pkl", "rb") as f:
    documents = pickle.load(f)

# 🔴 ADD YOUR API KEY HERE
client = MistralClient(api_key="vzkzUFJL9VoAS13Agc0SzUgJ4tETu9Dn")

# -------- CONNECT MONGODB --------
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["geoscience_db"]
collection = db["generated_qa"]

print("✅ Data Loaded Successfully")
print(f"📊 Total documents: {len(documents)}")

# -------- USER INPUT --------
save_csv = input("\nDo you want to save output as CSV? (yes/no): ").strip().lower()

# -------- CSV SETUP --------
writer = None
if save_csv == "yes":
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_qa_{timestamp}.csv"

    file = open(filename, "w", newline="", encoding="utf-8")
    writer = csv.writer(file)
    writer.writerow(["Question", "Answer", "Accuracy"])

    print(f"\n📁 CSV will be saved as: {filename}\n")
else:
    print("\n📌 CSV not selected\n")

# -------- GENERATE Q&A --------
num_questions = 3

for i in range(num_questions):

    print(f"\n=========== Q&A {i+1} ===========")

    # -------- STEP 1: RANDOM BASE CONTEXT --------
    base_doc = random.choice(documents)
    base_context = base_doc.get("answer", "")

    # -------- STEP 2: FAISS RETRIEVAL (RAG) --------
    query_embedding = model.encode([base_context])
    D, I = index.search(query_embedding, 3)

    context_list = []
    for idx in I[0]:
        if idx < len(documents):
            context_list.append(documents[idx].get("answer", ""))

    context = " ".join(context_list)

    print("\n📌 Retrieved Context:\n", context[:300], "...")

    # -------- STEP 3: GENERATE QUESTION --------
    question_prompt = f"""
You are a geoscience domain expert.

Generate ONE high-quality, precise, and meaningful question based strictly on the given context.

Requirements:
- Focus on conceptual or analytical understanding
- Avoid simple definitions and yes/no questions
- Ensure clarity and specificity
- Do NOT copy sentences from the context
- Maintain a professional tone

Context:
{context}

Output:
Return only the question.
"""

    response_q = client.chat(
        model="mistral-medium",
        messages=[ChatMessage(role="user", content=question_prompt)]
    )

    question = clean_text(response_q.choices[0].message.content)
    print("\n🧠 Question:\n", question)

    # -------- STEP 4: GENERATE ANSWER --------
    answer_prompt = f"""
You are a geoscience domain expert.

Provide a clear, accurate, and structured answer using ONLY the given context.

Requirements:
- Use 3–5 bullet points
- Keep it concise and informative
- Avoid repetition
- Do not include external knowledge
- If insufficient context, say:
  "Not enough information in the provided context."

Context:
{context}

Question:
{question}

Output:
Return only the structured answer.
"""

    response_a = client.chat(
        model="mistral-medium",
        messages=[ChatMessage(role="user", content=answer_prompt)]
    )

    answer = clean_text(response_a.choices[0].message.content)
    print("\n✅ Answer:\n", answer)

    # -------- STEP 5: EVALUATION --------
    evaluation_prompt = f"""
You are a geoscience evaluator.

Evaluate how accurate the answer is based on the context.

Return:
- Accuracy Score (0-100)
- One-line justification

Context:
{context}

Question:
{question}

Answer:
{answer}
"""

    response_eval = client.chat(
        model="mistral-medium",
        messages=[ChatMessage(role="user", content=evaluation_prompt)]
    )

    evaluation = clean_text(response_eval.choices[0].message.content)
    print("\n📊 Evaluation:\n", evaluation)

    # -------- EXTRACT NUMERIC SCORE --------
    score = None
    try:
        numbers = ''.join(filter(str.isdigit, evaluation))
        if numbers:
            score = int(numbers[:3])
    except:
        score = None

    # -------- SAVE TO CSV --------
    if writer:
        writer.writerow([question, answer, score])

    # -------- SAVE TO MONGODB --------
    data = {
        "context": context,
        "question": question,
        "answer": answer,
        "evaluation": evaluation,
        "accuracy_score": score,
        "created_at": datetime.datetime.now()
    }

    collection.insert_one(data)

# -------- CLOSE CSV --------
if save_csv == "yes":
    file.close()
    print("\n🎉 CSV file created successfully!")

print("\n📦 Data stored in MongoDB successfully!")
print("\n✅ Done!")