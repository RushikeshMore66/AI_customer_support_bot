import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

load_dotenv()

app = FastAPI(title="AI Customer Support Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def get_client_and_db():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    client = Groq(api_key=groq_api_key)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory="db", embedding_function=embeddings)
    return client, db

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        client, db = get_client_and_db()
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

    user_query = req.message
    docs = db.similarity_search(user_query, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a top-tier customer support agent similar to Amazon.

Behavior:
- Always be polite and professional
- Give clear step-by-step solutions
- Keep answers short but helpful
- If question is about refund/returns → explain process step-by-step
- If question is unclear → ask a follow-up question
- Never make up information outside context

Context:
{context}

User Question:
{user_query}

Answer in a helpful and human tone:
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional customer support assistant."},
                *req.history,
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content
        return {"reply": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        client, db = get_client_and_db()
        
        # Save uploaded file safely
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
        else:
            loader = TextLoader(temp_path)

        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)

        # Store in DB
        db.add_documents(docs)

        os.remove(temp_path)
        return {"message": "File uploaded and trained successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/whatsapp")
async def whatsapp_reply(Body: str = Form(...)):
    try:
        client, db = get_client_and_db()
        docs = db.similarity_search(Body, k=3)
        context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""
        You are a helpful WhatsApp support agent.
        Context:
        {context}
        Question:
        {Body}
        Answer:
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content

        return Response(
            content=f"<Response><Message>{answer}</Message></Response>",
            media_type="application/xml"
        )
    except Exception as e:
        return Response(content=f"<Response><Message>Error: {str(e)}</Message></Response>", media_type="application/xml")
