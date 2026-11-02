from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume, ResumeAnalysis
from app.schemas.resume import (
    ResumeAnalysisResponse,
    ResumeResponse,
    ResumeGenerateRequest,
    ResumeExtractedDataUpdate,
    ResumeCorrectionActionRequest,
    RoleOptimizeRequest,
    RoleOptimizeResponse,
    JobMatchRequest,
    JobMatchResponse
)
from app.services.auth_service import get_current_user
from app.services.resume_service import resume_service
from app.core.security import (
    validate_resume_file,
    safe_extract_pdf_text,
    safe_extract_docx_text,
    secure_delete_file,
    sanitize_input_text
)

router = APIRouter(prefix="/resumes", tags=["Resumes & ATS Engine"])

def _format_analysis_response(analysis: ResumeAnalysis, extracted_data: Optional[Dict[str, Any]] = None) -> ResumeAnalysisResponse:
    return ResumeAnalysisResponse(
        id=analysis.id,
        resume_id=analysis.resume_id,
        target_role=analysis.target_role,
        overall_ats_score=round(analysis.overall_ats_score or 0.0, 1),
        keyword_match_score=round(analysis.keyword_match_score or 0.0, 1),
        structure_score=round(analysis.structure_score or 0.0, 1),
        impact_score=round(analysis.impact_score or 0.0, 1),
        readability_score=round((analysis.readability_metrics or {}).get("score", 78.0), 1),
        section_scores=analysis.section_scores or {},
        matched_skills=analysis.matched_skills or [],
        missing_skills=analysis.missing_skills or [],
        missing_keywords=analysis.missing_skills or [],
        grammar_errors=analysis.grammar_errors or [],
        weak_sentences=analysis.weak_sentences or [],
        formatting_issues=analysis.formatting_issues or [],
        action_verb_suggestions=analysis.action_verb_suggestions or [],
        improvement_recommendations=(analysis.formatting_issues or [])[:3],
        corrections=analysis.corrections or [],
        section_breakdown=analysis.section_breakdown or {},
        readability_metrics=analysis.readability_metrics or {},
        extracted_data=extracted_data or (analysis.resume.parsed_data if analysis.resume else None),
        disclaimer=analysis.disclaimer or (
            "Notice: Estimated ATS compatibility scores are heuristic benchmarks based on standard parsing algorithms, "
            "structural completeness, and keyword weighting. They are not guaranteed results for any specific proprietary commercial ATS."
        ),
        detailed_feedback=analysis.detailed_feedback or "",
        created_at=analysis.created_at
    )

@router.post("/analyze-upload", response_model=ResumeAnalysisResponse)
async def analyze_uploaded_resume(
    file: UploadFile = File(...),
    target_role: str = Form("Full Stack Software Engineer"),
    job_description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    
    # 1. File size restrictions and magic byte verification
    verified_fmt = validate_resume_file(contents, file.filename)
    
    # 2. Safe Document Parsing (defending against decompression bombs and infinite loops)
    if verified_fmt == "pdf":
        resume_text = safe_extract_pdf_text(contents)
    elif verified_fmt == "docx":
        resume_text = safe_extract_docx_text(contents)
    else:
        resume_text = contents.decode("utf-8", errors="ignore")

    # 3. Input Sanitization
    resume_text = sanitize_input_text(resume_text, max_length=200000)
    target_role = sanitize_input_text(target_role, max_length=150)
    if job_description:
        job_description = sanitize_input_text(job_description, max_length=50000)

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable text from the uploaded document.")

    # Run comprehensive ATS analysis & extraction
    analysis_dict = resume_service.analyze_resume(
        resume_text=resume_text,
        target_role=target_role,
        job_description=job_description
    )

    # Save Resume record with full extracted data
    resume_record = Resume(
        user_id=current_user.id,
        title=file.filename,
        target_role=target_role,
        raw_text=resume_text,
        file_name=file.filename,
        parsed_data=analysis_dict["extracted_data"]
    )
    db.add(resume_record)
    db.commit()
    db.refresh(resume_record)

    # Save Analysis record
    analysis_record = ResumeAnalysis(
        resume_id=resume_record.id,
        user_id=current_user.id,
        target_role=target_role,
        job_description=job_description,
        overall_ats_score=analysis_dict["overall_ats_score"],
        keyword_match_score=analysis_dict["keyword_match_score"],
        structure_score=analysis_dict["structure_score"],
        impact_score=analysis_dict["impact_score"],
        matched_skills=analysis_dict["matched_skills"],
        missing_skills=analysis_dict["missing_skills"],
        formatting_issues=analysis_dict["formatting_issues"],
        action_verb_suggestions=analysis_dict["action_verb_suggestions"],
        section_breakdown=analysis_dict["section_breakdown"],
        section_scores=analysis_dict["section_scores"],
        grammar_errors=analysis_dict["grammar_errors"],
        weak_sentences=analysis_dict["weak_sentences"],
        corrections=analysis_dict["corrections"],
        readability_metrics=analysis_dict["readability_metrics"],
        disclaimer=analysis_dict["disclaimer"],
        detailed_feedback=analysis_dict["detailed_feedback"]
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    return _format_analysis_response(analysis_record, extracted_data=analysis_dict["extracted_data"])

@router.post("/analyze-text", response_model=ResumeAnalysisResponse)
def analyze_resume_text(
    target_role: str = Form("Full Stack Software Engineer"),
    resume_text: str = Form(...),
    job_description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume_text = sanitize_input_text(resume_text, max_length=200000)
    target_role = sanitize_input_text(target_role, max_length=150)
    if job_description:
        job_description = sanitize_input_text(job_description, max_length=50000)

    if len(resume_text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Please provide a valid resume text (at least 30 characters).")

    analysis_dict = resume_service.analyze_resume(
        resume_text=resume_text,
        target_role=target_role,
        job_description=job_description
    )

    resume_record = Resume(
        user_id=current_user.id,
        title=f"Resume - {target_role}",
        target_role=target_role,
        raw_text=resume_text,
        file_name="pasted_text.txt",
        parsed_data=analysis_dict["extracted_data"]
    )
    db.add(resume_record)
    db.commit()
    db.refresh(resume_record)

    analysis_record = ResumeAnalysis(
        resume_id=resume_record.id,
        user_id=current_user.id,
        target_role=target_role,
        job_description=job_description,
        overall_ats_score=analysis_dict["overall_ats_score"],
        keyword_match_score=analysis_dict["keyword_match_score"],
        structure_score=analysis_dict["structure_score"],
        impact_score=analysis_dict["impact_score"],
        matched_skills=analysis_dict["matched_skills"],
        missing_skills=analysis_dict["missing_skills"],
        formatting_issues=analysis_dict["formatting_issues"],
        action_verb_suggestions=analysis_dict["action_verb_suggestions"],
        section_breakdown=analysis_dict["section_breakdown"],
        section_scores=analysis_dict["section_scores"],
        grammar_errors=analysis_dict["grammar_errors"],
        weak_sentences=analysis_dict["weak_sentences"],
        corrections=analysis_dict["corrections"],
        readability_metrics=analysis_dict["readability_metrics"],
        disclaimer=analysis_dict["disclaimer"],
        detailed_feedback=analysis_dict["detailed_feedback"]
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    return _format_analysis_response(analysis_record, extracted_data=analysis_dict["extracted_data"])

@router.get("/{resume_id}/extracted")
def get_extracted_resume_data(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {
        "resume_id": resume.id,
        "title": resume.title,
        "target_role": resume.target_role,
        "extracted_data": resume.parsed_data or {}
    }

@router.put("/{resume_id}/extracted", response_model=ResumeAnalysisResponse)
def update_extracted_resume_data(
    resume_id: int,
    update_data: ResumeExtractedDataUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Update parsed data
    new_data = update_data.extracted_data.dict()
    resume.parsed_data = new_data
    if new_data.get("full_name"):
        resume.title = f"Resume - {new_data['full_name']}"

    # Construct synthesized resume text for fresh ATS evaluation
    text_blocks = [
        new_data.get("full_name", ""),
        new_data.get("email", ""),
        new_data.get("phone", ""),
        new_data.get("summary", ""),
        "EDUCATION:"
    ]
    for edu in new_data.get("education", []):
        text_blocks.append(f"{edu.get('degree', '')} at {edu.get('institution', '')} {edu.get('year', '')}")
    text_blocks.append("EXPERIENCE:")
    for exp in new_data.get("work_experience", []):
        text_blocks.append(f"{exp.get('role', '')} at {exp.get('company', '')} ({exp.get('duration', '')})")
        for h in exp.get("highlights", []):
            text_blocks.append(f"• {h}")
    text_blocks.append("SKILLS:")
    for cat, sk_list in new_data.get("technical_skills", {}).items():
        text_blocks.append(f"{cat}: {', '.join(sk_list)}")
    text_blocks.append("PROJECTS:")
    for p in new_data.get("projects", []):
        text_blocks.append(f"{p.get('name', '')}: {p.get('description', '')}")

    synth_text = "\n".join(text_blocks)
    resume.raw_text = synth_text
    db.commit()

    # Re-evaluate with updated data
    analysis_dict = resume_service.analyze_resume(
        resume_text=synth_text,
        target_role=resume.target_role or "Full Stack Software Engineer"
    )

    new_analysis = ResumeAnalysis(
        resume_id=resume.id,
        user_id=current_user.id,
        target_role=resume.target_role or "Full Stack Software Engineer",
        overall_ats_score=analysis_dict["overall_ats_score"],
        keyword_match_score=analysis_dict["keyword_match_score"],
        structure_score=analysis_dict["structure_score"],
        impact_score=analysis_dict["impact_score"],
        matched_skills=analysis_dict["matched_skills"],
        missing_skills=analysis_dict["missing_skills"],
        formatting_issues=analysis_dict["formatting_issues"],
        action_verb_suggestions=analysis_dict["action_verb_suggestions"],
        section_breakdown=analysis_dict["section_breakdown"],
        section_scores=analysis_dict["section_scores"],
        grammar_errors=analysis_dict["grammar_errors"],
        weak_sentences=analysis_dict["weak_sentences"],
        corrections=analysis_dict["corrections"],
        readability_metrics=analysis_dict["readability_metrics"],
        disclaimer=analysis_dict["disclaimer"],
        detailed_feedback="Updated based on user edits to extracted resume sections."
    )
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return _format_analysis_response(new_analysis, extracted_data=new_data)

@router.post("/{analysis_id}/corrections/{correction_id}")
def handle_correction_action(
    analysis_id: int,
    correction_id: str,
    payload: ResumeCorrectionActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis_id, ResumeAnalysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    corrections = list(analysis.corrections or [])
    updated = False
    for c in corrections:
        if str(c.get("id")) == str(correction_id):
            c["status"] = "accepted" if payload.action == "accept" else "rejected"
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Correction ID not found")

    analysis.corrections = corrections
    db.commit()

    return {"status": "success", "correction_id": correction_id, "action": payload.action, "corrections": corrections}

@router.get("/", response_model=List[ResumeResponse])
def get_user_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()

@router.get("/{resume_id}/analyses", response_model=List[ResumeAnalysisResponse])
def get_resume_analyses(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analyses = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume_id, ResumeAnalysis.user_id == current_user.id).order_by(ResumeAnalysis.created_at.desc()).all()
    return [_format_analysis_response(a) for a in analyses]

@router.post("/match-job-description", response_model=JobMatchResponse)
def match_job_description_endpoint(
    payload: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume_text = payload.resume_text or ""
    if not resume_text and payload.resume_id:
        resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
        if resume:
            resume_text = resume.raw_text or ""

    if not resume_text:
        latest = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
        if latest:
            resume_text = latest.raw_text or ""

    if not resume_text:
        raise HTTPException(status_code=400, detail="Please upload or paste a resume to compare against the job description.")

    if len(payload.job_description.strip()) < 30:
        raise HTTPException(status_code=400, detail="Please paste a valid job description (at least 30 characters).")

    result = resume_service.match_job_description(
        resume_text=resume_text,
        job_description=payload.job_description,
        target_role=payload.target_role or "Software Engineer"
    )
    return JobMatchResponse(**result)

@router.post("/optimize-role", response_model=RoleOptimizeResponse)
def optimize_resume_for_role(
    payload: RoleOptimizeRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        result = resume_service.optimize_for_role(payload.dict())
        return RoleOptimizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to optimize resume for role: {str(e)}")

@router.post("/generate-pdf")
def generate_ats_pdf(
    resume_data: ResumeGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        pdf_bytes = resume_service.generate_pdf_resume(resume_data.dict())
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=ATS_Resume_{resume_data.full_name.replace(' ', '_')}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ATS PDF: {str(e)}")

@router.post("/generate-docx")
def generate_ats_docx(
    resume_data: ResumeGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        docx_bytes = resume_service.generate_docx_resume(resume_data.dict())
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=ATS_Resume_{resume_data.full_name.replace(' ', '_')}.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ATS DOCX: {str(e)}")

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Secure File Deletion & User Data Isolation:
    1. Verifies that the requested resume belongs strictly to current_user (isolation).
    2. Securely shreds physical file content on disk with random byte overwrite before unlinking.
    3. Cascades deletion of associated analysis records.
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume record not found or access denied.")

    # Secure shredding if on-disk file path exists
    if hasattr(resume, "file_path") and resume.file_path:
        secure_delete_file(resume.file_path)

    # Cascade delete analyses
    db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume.id).delete()

    db.delete(resume)
    db.commit()

    return {
        "status": "success",
        "message": f"Resume #{resume_id} and associated ATS records securely deleted."
    }
