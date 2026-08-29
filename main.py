from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import pypdf
import io
import json
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY .env file me nahi mili!")

client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="AI ATS Resume Matcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Sirf PDF files supported hain.")

    pdf_bytes = await resume.read()
    resume_text = extract_text_from_pdf(pdf_bytes)

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="PDF se text extract nahi ho paya.")

    prompt = f"""
    You are an expert HR and ATS (Applicant Tracking System) specialist.
    Analyze the following candidate's Resume against the provided Job Description.

    Candidate Resume:
    {resume_text}

    Target Job Description:
    {job_description}

    Provide the output strictly in valid JSON format with these exact keys:
    {{
        "match_score": <integer score between 0 and 100>,
        "summary": "<2-3 sentence overview of candidate suitability>",
        "missing_skills": ["<skill 1>", "<skill 2>"],
        "strengths": ["<strength 1>", "<strength 2>"],
        "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"]
    }}
    Do not wrap the output in code markdown. Return pure JSON only.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        response_clean = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_clean)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def home():
    return {"message": "AI ATS Backend server is running successfully!"}