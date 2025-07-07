from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Query
from backend.document_processor import DocumentProcessor
from backend.qa_system import QASystem
from pydantic import BaseModel
import uuid
from datetime import datetime  # Import for datetime
from fastapi import HTTPException
from pydantic import BaseModel

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
processor = DocumentProcessor()
qa_system = QASystem()

# Temporary storage for documents
documents = {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Research Assistant API</title>
        </head>
        <body>
            <h1>Research Assistant API</h1>
            <p>The API is running. Use the following endpoints:</p>
            <ul>
                <li><a href="/docs">/docs</a> - API documentation</li>
                <li><a href="/redoc">/redoc</a> - Alternative documentation</li>
                <li>/upload - POST endpoint for document upload</li>
                <li>/ask/{doc_id} - POST endpoint for questions</li>
                <li>/challenge/{doc_id} - GET endpoint for challenges</li>
            </ul>
            <p>Frontend should be running at <a href="http://localhost:8501">http://localhost:8501</a></p>
        </body>
    </html>
    """



@app.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Get clean lowercase extension
        filename = file.filename
        file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        # Verify both extension and content type
        is_pdf = (file_ext == 'pdf') or (file.content_type == 'application/pdf')
        is_txt = (file_ext == 'txt') or (file.content_type == 'text/plain')
        
        if not (is_pdf or is_txt):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Only PDF and TXT files are accepted"
            )
        
        # Additional PDF validation
        if is_pdf:
            # Read first 4 bytes to verify PDF magic number
            header = await file.read(4)
            await file.seek(0)  # Rewind for actual processing
            if header != b'%PDF':
                raise HTTPException(
                    status_code=400,
                    detail="Invalid PDF file (missing PDF header)"
                )
        
        # Read file content
        contents = await file.read()
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Process the file based on type
        if is_pdf:
            text = processor.process_pdf(contents)
        else:
            text = processor.process_text(contents)
        
        # Store document
        documents[doc_id] = {
            "text": text,
            "filename": filename,
            "upload_time": datetime.now().isoformat()
        }
        
        # Generate initial summary
        summary = qa_system.generate_summary(text)
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "filename": filename,
            "summary": summary,
            "message": "Document processed successfully"
        }
        
    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Text file contains invalid characters (not UTF-8 encoded)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/ask/{doc_id}")
async def ask_question(doc_id: str, question: str):
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    text = documents[doc_id]["text"]
    answer, justification = qa_system.answer_question(text, question)
    
    return {
        "answer": answer,
        "justification": justification
    }


@app.get("/challenge/{doc_id}")
def challenge_me(doc_id: str):
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        text = documents[doc_id]["text"]  # ✅ corrected key here
        print(f"Challenge request received for doc_id: {doc_id}")
        questions = qa_system.generate_questions(text)
        if not questions:
            raise HTTPException(status_code=500, detail="No questions could be generated.")
        return {"questions": questions}
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")


class AnswerRequest(BaseModel):
    answer: str

@app.post("/evaluate/{doc_id}/{question_id}")
async def evaluate_answer(doc_id: str, question_id: int, request: AnswerRequest):
    answer = request.answer
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    text = documents[doc_id]["text"]
    evaluation = qa_system.evaluate_answer(text, question_id, answer)
    return {"evaluation": evaluation}
    
def get_question_by_id(self, doc_id, question_id):
    try:
        return self.generated_questions[doc_id][question_id]
    except:
        return "Question not found."
