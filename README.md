# 🌍 Geoscience AI Research Assistant

##  Project Overview
An AI-powered geoscience assistant that retrieves and answers domain-specific queries using web-scraped data, vector search, and LLMs.

The system follows a complete pipeline from data collection to intelligent response generation.

---

##  Features
-  Web scraping of geoscience data  
-  Data cleaning and preprocessing  
-  Structured Q&A generation  
-  Semantic search using FAISS  
-  MongoDB for storing processed data  
-  LLM-powered answer generation (Mistral API)  
-  FastAPI backend for APIs  
-  React frontend for user interaction  

---

##  Tech Stack
- **Backend:** FastAPI, Python  
- **Frontend:** React.js  
- **Database:** MongoDB  
- **Vector Store:** FAISS  
- **ML/NLP:** Sentence Transformers  
- **LLM:** Mistral API  

---

## 📂 Project Structure
geoscience_pipeline/
│── api.py  
│── main.py  
│── requirements.txt  
│── README.md  
│  
├── crawler/  
├── embeddings/  
├── processing/  
├── vector_store/  
├── frontend/  

---

##  Setup Instructions

### 🔹 Backend Setup
pip install -r requirements.txt  

### 🔹 Frontend Setup
cd frontend  
npm install  

### 🔹 Database Setup (MongoDB)
- Make sure MongoDB is running locally  
- Default: mongodb://localhost:27017  

---

## ▶️ Run the Project

### 🔹 Start Backend (FastAPI)
uvicorn api:app --reload  

### 🔹 Start Frontend (React)
cd frontend  
npm start  

---

##  Application URLs
- Backend → http://127.0.0.1:8000  
- Frontend → http://localhost:3000  

---

##  How It Works
1. Scrapes geoscience data using crawler  
2. Cleans and processes data  
3. Stores structured data in MongoDB  
4. Generates embeddings using Sentence Transformers  
5. Stores vectors in FAISS  
6. Retrieves relevant context  
7. Uses Mistral LLM to generate answers  

---

##  Future Improvements
- Add authentication system  
- Deploy on cloud  
- Improve UI/UX  
- Add real-time data pipeline  

---

##  Author
Vaishnavi Ragunath