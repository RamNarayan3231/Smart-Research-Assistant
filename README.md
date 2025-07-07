
# 📚 Smart Research Assistant

An AI-powered web application that allows users to upload research documents (PDF/TXT), ask questions, receive AI-generated answers with justifications, and evaluate their own understanding through generated challenge questions and feedback.

## 🔧 Features

✅ Upload PDF or TXT documents

✅ AI-generated document summary

✅ Ask contextual questions about the document

✅ Generate challenge questions to test comprehension

✅ Answer evaluation with scoring and ideal answers

✅ Clean UI using Streamlit

✅ FastAPI backend with LLM integration via OpenRouter


## 🚀 Demo


![Screenshot 2025-07-08 022512](https://github.com/user-attachments/assets/b56fd6e5-a245-491f-a1eb-7f0ed7154327)

![Screenshot 2025-07-08 022853](https://github.com/user-attachments/assets/f9e723c0-86c1-4293-876d-5330620a9f26)

![Screenshot 2025-07-08 020632](https://github.com/user-attachments/assets/4dbff42b-cad7-4e5d-9e28-79e873f6736e)

![Screenshot 2025-07-08 042502](https://github.com/user-attachments/assets/8fc1eb1a-1856-426b-bcf5-ecb33798cef7)

![Screenshot 2025-07-08 022947](https://github.com/user-attachments/assets/4c946bc7-b2d2-4218-b397-bd10783b9325)

![Screenshot 2025-07-08 024621](https://github.com/user-attachments/assets/fa57cf14-b800-4e51-91ac-073f5b54c185)



## 📁 Project Structure

```
research-assistant/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI backend entry point
│   ├── document_processor.py  # PDF/TXT parsing and summarization
│   ├── openrouter_llm.py      # Custom LLM interface using OpenRouter
│   ├── qa_system.py           # Handles QA, challenge generation, evaluation
│   └── utils.py               # Utilities (text cleaning, word count, etc.)
│
├── frontend/
│   └── app.py                 # Streamlit frontend app
│
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── venv/                      # Virtual environment (optional)
```


## 🚀 How to Run

### 1. Clone the Repository
```
git clone https://github.com/RAmNarayan3231/Smart-Research-Assistant.git
cd research-assistant
```
### 2. Set up Environment
Create a .env file in the root directory and include the following:
```
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4.1-nano
YOUR_SITE_URL=http://localhost:8501
YOUR_SITE_NAME=Smart Research Assistant
```
### 3. Install Dependencies
```
pip install -r requirements.txt
```


## 🖥️ Running the App

### Step 1: Start Backend
```
uvicorn main:app --reload
```
It will start at http://localhost:8000.

### Step 2: Start Frontend
```
streamlit run frontend/app.py
```
It will launch the frontend at http://localhost:8501.

# 🛠️ API Endpoints

Method	Endpoint	Description
POST	/upload/	Upload and process a document
POST	/ask/{doc_id}	Ask a question about a document
GET	/challenge/{doc_id}	Generate challenge questions
POST	/evaluate/{doc_id}/{id}	Evaluate user's answer
GET	/	API homepage



## 📚 Technologies 

Python 3.10+
Streamlit – for interactive frontend
FastAPI – for robust backend APIs
LangChain – for chaining LLM prompts
OpenRouter – LLM API provider
PyPDF2 – for PDF reading
Pydantic – for data validation

## 🧠 Future Improvements

✅ Semantic search for better QA context
✅ PDF OCR (for scanned PDFs)
✅ Save sessions and history
✅ MCQ generation
✅ Multilingual support

## 🤝 Contributing
Feel free to fork the repo and submit pull requests. For major changes, open an issue first.

