import os
import json
import io
import re
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

def clean_json_response(raw_text: str) -> dict:
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        clean_str = match.group(0)
    else:
        clean_str = raw_text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_str)

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
    You are an expert ATS scanner. Analyze this resume against the JD.
    
    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Return ONLY a valid raw JSON object. No conversation, no markdown code block:
    {{
        "match_score": 78,
        "matched_skills": ["Skill1", "Skill2"],
        "missing_skills": ["Skill3", "Skill4"],
        "recommendations": ["Recommendation1"]
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        data = clean_json_response(response.text)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Processing Error: {str(e)}")

@app.post("/improve-bullets")
async def improve_bullets(resume: UploadFile = File(...), job_description: str = Form(...)):
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    prompt = f"""
    You are an expert ATS resume editor. Do NOT invent fake companies or positions.
    Identify 3 to 5 weak bullet points or project details from this resume and rewrite them to naturally incorporate keywords from the JD.
    
    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Return ONLY a valid raw JSON object. No conversation, no markdown code block:
    {{
        "improved_bullets": [
            {{
                "original": "Original line from resume",
                "improved": "High-impact ATS-friendly rewritten line",
                "reason": "Why this aligns better with the target role"
            }}
        ]
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        data = clean_json_response(response.text)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Processing Error: {str(e)}")