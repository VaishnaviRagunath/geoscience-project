from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pymongo import MongoClient
import datetime
import io
import re
import csv

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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


# 🔥 ASK API (CLEAN - NO EVALUATION)
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
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\*", "", text)
    text = re.sub(r"`", "", text)
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"-", "•", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()


# 🔥 PDF EXPORT
@app.post("/export-pdf")
def export_pdf(data: dict):

    content = data.get("content", "")
    question = data.get("question", "Geoscience_Response")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Geoscience Chatbot Response", styles["Title"]))
    story.append(Spacer(1, 12))

    # Question
    story.append(Paragraph("<b>User Question:</b>", styles["Heading2"]))
    story.append(Paragraph(question, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Answer
    story.append(Paragraph("<b>Answer:</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))

    clean_text = clean_markdown(content)
    paragraphs = clean_text.split("\n\n")

    for para in paragraphs:

        # Table detection
        if "|" in para and "---" in para:
            lines = para.split("\n")
            table_data = []

            for line in lines:
                if "|" in line:
                    row = [cell.strip() for cell in line.split("|") if cell.strip()]
                    if row:
                        table_data.append(row)

            if table_data:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(table)
                story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(para.strip(), styles["Normal"]))
            story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=response.pdf"}
    )


# 🔥 CSV EXPORT
@app.post("/export-csv")
def export_csv(data: dict):

    content = data.get("content", "")
    question = data.get("question", "")

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Question", "Answer"])

    # Content
    clean_text = clean_markdown(content)
    writer.writerow([question, clean_text])

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=response.csv"}
    )