from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pymongo import MongoClient
import datetime
import io
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from vector_store.geoscience_assistant import retrieve_context, ask_mistral

app = FastAPI()

# ✅ MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["geoscience_db"]
collection = db["chat_history"]

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request model
class QuestionRequest(BaseModel):
    user_id: str
    question: str


@app.get("/")
def home():
    return {"message": "API working"}


# 🔥 FIXED (NO ASYNC ISSUE)
@app.post("/ask")
def ask_question(req: QuestionRequest):

    question = req.question
    user_id = req.user_id

    print("➡️ Getting context...")
    context, sources = retrieve_context(question)

    print("➡️ Calling Mistral...")
    answer = ask_mistral(question, context)

    print("✅ Response ready")

    # Save to MongoDB
    collection.insert_one({
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "sources": sources[:3],
        "timestamp": datetime.datetime.utcnow()
    })

    return {
        "answer": answer,
        "sources": sources[:3]
    }


# 🔥 HISTORY
@app.get("/history/{user_id}")
def get_history(user_id: str):
    chats = list(collection.find({"user_id": user_id}).sort("timestamp", -1))

    for chat in chats:
        chat["_id"] = str(chat["_id"])

    return chats


# 🔥 CLEAN MARKDOWN
def clean_markdown(text: str) -> str:
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\*", "", text)
    text = re.sub(r"`", "", text)
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"-", "•", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text


# 🔥 PDF EXPORT
@app.post("/export-pdf")
def export_pdf(data: dict):

    content = data.get("content", "")

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        title="Geoscience Chatbot Response",
        author="Geoscience AI"
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Geoscience Chatbot Response", styles["Title"]))
    story.append(Spacer(1, 12))

    clean_text = clean_markdown(content)

    for line in clean_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), styles["Normal"]))
            story.append(Spacer(1, 8))

    doc.build(story)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=response.pdf"}
    )