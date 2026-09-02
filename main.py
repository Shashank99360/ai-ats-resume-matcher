import os
import json
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="AI ATS Resume Matcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    pdf_reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

@app.get("/")
async def serve_home():
    return FileResponse("index.html")

@app.post("/analyze")
async def analyze_resume(resume: UploadFile = File(...), job_description: str = Form(...)):
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    prompt = f"""
    You are an expert ATS scanner. Analyze this resume against the JD:
    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Return JSON only without markdown backticks:
    {{
        "match_score": 75,
        "matched_skills": ["Skill 1", "Skill 2"],
        "missing_skills": ["Skill 3", "Skill 4"],
        "recommendations": ["Recommendation 1", "Recommendation 2"]
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        return {"status": "success", "data": json.loads(cleaned)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/improve-bullets")
async def improve_bullets(resume: UploadFile = File(...), job_description: str = Form(...)):
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    prompt = f"""
    You are an elite ATS resume optimizer. Do NOT change the user's career facts, company names, or resume structure.
    Find specific weak bullet points or project lines in this resume that miss keywords from the Job Description, and rewrite ONLY those lines to be high-impact, keyword-rich, and metric-driven.

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Return response STRICTLY in valid JSON without backticks:
    {{
        "improved_bullets": [
            {{
                "original": "Original line from resume",
                "improved": "Rewritten ATS-optimized line with JD keywords",
                "reason": "Why this improves ATS ranking"
            }}
        ]
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        return {"status": "success", "data": json.loads(cleaned)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))