
#📚 Smart Research Assistant

An AI-powered web application that allows users to upload research documents (PDF/TXT), ask questions, receive AI-generated answers with justifications, and evaluate their own understanding through generated challenge questions and feedback.

##🔧 Features
✅ Upload PDF or TXT documents

✅ AI-generated document summary

✅ Ask contextual questions about the document

✅ Generate challenge questions to test comprehension

✅ Answer evaluation with scoring and ideal answers

✅ Clean UI using Streamlit

✅ FastAPI backend with LLM integration via OpenRouter



##📁 Project Structure

research-assistant/
│
├── backend/
│   ├── __init__.py
│   ├── document_processor.py   # PDF/TXT parsing and summarization
│   ├── openrouter_llm.py       # Custom LLM interface using OpenRouter
│   ├── qa_system.py            # Handles QA, challenge generation, evaluation
|   ├── main.py                 # FastAPI backend app
│   └── utils.py                # Utilities (text cleaning, word count, etc.)
│
├── frontend/
│   └── app.py                  # Streamlit frontend app
│
├── requirements.txt            # Python dependencies
└── venv/                       # Virtual environment (optional)




#🚀 How to Run

1. Clone the Repository

git clone https://github.com/your-username/research-assistant.git
cd research-assistant

2. Set up Environment

3. Create a .env file in the root directory and include the following:

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4.1-nano
YOUR_SITE_URL=http://localhost:8501
YOUR_SITE_NAME=Smart Research Assistant

3. Install Dependencies

pip install -r requirements.txt



#🖥️ Running the App

Step 1: Start Backend

uvicorn main:app --reload
It will start at http://localhost:8000.

Step 2: Start Frontend

streamlit run frontend/app.py
It will launch the frontend at http://localhost:8501.

#🛠️ API Endpoints
Method	Endpoint	Description
POST	/upload/	Upload and process a document
POST	/ask/{doc_id}	Ask a question about a document
GET	/challenge/{doc_id}	Generate challenge questions
POST	/evaluate/{doc_id}/{id}	Evaluate user's answer
GET	/	API homepage



#📸 Screenshots 



#📚 Technologies 

Python 3.10+

Streamlit – for interactive frontend

FastAPI – for robust backend APIs

LangChain – for chaining LLM prompts

OpenRouter – LLM API provider

PyPDF2 – for PDF reading

Pydantic – for data validation



#🧠 Future Improvements

✅ Semantic search for better QA context

✅ PDF OCR (for scanned PDFs)

✅ Save sessions and history

✅ MCQ generation

✅ Multilingual support



#🤝 Contributing
Feel free to fork the repo and submit pull requests. For major changes, open an issue first.

