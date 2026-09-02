# AI ATS Resume Matcher & Optimizer

An intelligent, full-stack ATS (Applicant Tracking System) platform that evaluates resumes against job descriptions, provides keyword compatibility scoring, and rewrites bullet points for maximum ATS impact with zero formatting loss.

🚀 **Live Demo**: [https://ai-ats-resume-matcher.onrender.com](https://ai-ats-resume-matcher.onrender.com)

---

## 🌟 Key Features

- **ATS Match Scoring**: Evaluates keyword alignment and role compatibility between a PDF resume and a target job description.
- **Skill Gap Analysis**: Highlights matched vs missing technical and soft skills.
- **Targeted Bullet Enhancer**: Rewrites resume bullet points with action verbs and JD keywords without disrupting original layout or styling.
- **1-Click Copy**: Allows quick replacement of optimized lines into your existing resume template.
- **Zero Formatting Distortion**: Preserves user document design by avoiding direct PDF alteration.

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **AI Engine**: Google Gemini API (`gemini-2.5-flash`)
- **PDF Extraction**: PyPDF
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript (Fetch API)
- **Deployment**: Render

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the web interface |
| `POST` | `/analyze` | Returns match score, matched skills, and missing skills |
| `POST` | `/improve-bullets` | Returns ATS-optimized rewrites for weak resume bullets |

---


## 💻 Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Shashank99360/ai-ats-resume-matcher.git](https://github.com/Shashank99360/ai-ats-resume-matcher.git)
   cd ai-ats-resume-matcher
   