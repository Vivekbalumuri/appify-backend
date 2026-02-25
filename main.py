from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from ml_client import call_ml_service

app = FastAPI(title="Appify Backend API 🚀")


# ---------- Request Model ----------

class Education(BaseModel):
    degree: str | None = None
    year: str | None = None
    cgpa: str | None = None


class Project(BaseModel):
    title: str | None = None
    description: str | None = None


class Experience(BaseModel):
    role: str | None = None
    duration: str | None = None


class ResumeData(BaseModel):
    user_id: str
    name: str
    email: str
    skills: List[str]
    education: List[Education] = []
    projects: List[Project] = []
    experience: List[Experience] = []
    raw_text: str


# ---------- Routes ----------

@app.get("/")
def home():
    return {"message": "Appify Backend Running Successfully 🚀"}


@app.post("/analyze")
def analyze_resume(data: ResumeData):

    try:
        ml_result = call_ml_service(data.model_dump())

        if "error" in ml_result:
            raise HTTPException(status_code=500, detail=ml_result["error"])

        return {
            "status": "success",
            "user_id": data.user_id,
            "analysis": ml_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))