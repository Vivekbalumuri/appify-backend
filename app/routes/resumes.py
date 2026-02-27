from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Resume
from app.utils.security import get_current_user
from app.services.ml_service import call_ml_service
from app.utils.pdf_parser import extract_text_from_pdf

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload")
async def analyze_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_bytes = await file.read()
    
    # 5MB limit
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")

    # Extract text
    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in PDF")

    ml_payload = {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "raw_text": raw_text
    }

    try:
        ml_result = await call_ml_service(ml_payload)
    except Exception as e:
        # In case the ML service is down, maybe we mock or fail. Let's fail with 500
        raise HTTPException(status_code=500, detail=f"ML Service error: {str(e)}")

    resume = Resume(
        user_id=current_user.id,
        raw_text=raw_text,
        skill_score=ml_result.get("skill_score"),
        experience_score=ml_result.get("experience_score"),
        project_score=ml_result.get("project_score"),
        education_score=ml_result.get("education_score"),
        ats_score=ml_result.get("ats_score"),
        final_score=ml_result.get("final_score"),
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "message": "Resume uploaded and analyzed successfully",
        "resume_id": resume.id,
        "analysis": ml_result
    }