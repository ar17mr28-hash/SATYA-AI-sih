import datetime
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import (
    User, Institution, Application, Document, DocumentExtraction,
    VerificationFinding, ComplianceRule, ComplianceResult, ReviewDecision,
    Notification, AuditLog
)
from ..schemas.schemas import (
    ApplicationCreate, ApplicationUpdate, ApplicationOut, ApplicationDetailOut
)
from ..services.auth import get_current_user, log_audit
from ..ai.consistency import ConsistencyEngine
from ..ai.compliance_engine import ComplianceEngine

router = APIRouter(prefix="/applications", tags=["Applications"])

def execute_ai_validation_pipeline(app_id: int, db: Session):
    """
    Executes full AI Document Intelligence, Cross-Document Consistency,
    and Regulatory Compliance Pipeline on the application.
    """
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        return

    institution = db.query(Institution).filter(Institution.id == app.institution_id).first()
    documents = db.query(Document).filter(Document.application_id == app.id).all()

    # Clear previous automated findings & compliance results for clean re-audit
    db.query(VerificationFinding).filter(VerificationFinding.application_id == app.id).delete()
    db.query(ComplianceResult).filter(ComplianceResult.application_id == app.id).delete()
    db.commit()

    # Prepare document data
    docs_payload = []
    uploaded_doc_types = []
    for d in documents:
        uploaded_doc_types.append(d.document_type)
        extr_data = {}
        if d.extraction:
            extr_data = {
                "extracted_fields": d.extraction.extracted_fields or {},
                "raw_text": d.extraction.raw_text or "",
                "confidence_score": d.extraction.confidence_score
            }
        docs_payload.append({
            "id": d.id,
            "document_type": d.document_type,
            "filename": d.filename,
            "extraction": extr_data
        })

    app_data = {
        "student_intake": app.student_intake,
        "faculty_count": app.faculty_count,
        "campus_area_acres": app.campus_area_acres,
        "built_up_area_sqm": app.built_up_area_sqm
    }
    inst_data = {
        "name": institution.name if institution else "",
        "code": institution.code if institution else ""
    }

    # 1. Run Consistency Engine
    detected_findings = ConsistencyEngine.audit_application_consistency(
        application_data=app_data,
        institution_data=inst_data,
        documents_with_extractions=docs_payload
    )

    created_findings = []
    for f in detected_findings:
        finding_obj = VerificationFinding(
            application_id=app.id,
            document_id=f.get("document_id"),
            finding_type=f.get("finding_type", "inconsistency"),
            title=f.get("title"),
            severity=f.get("severity", "warning"),
            explanation=f.get("explanation"),
            recommended_action=f.get("recommended_action"),
            evidence_snippet=f.get("evidence_snippet"),
            source_doc_title=f.get("source_doc_title"),
            page_number=f.get("page_number", 1)
        )
        db.add(finding_obj)
        created_findings.append(f)
    db.commit()

    # 2. Run Regulatory Compliance Engine
    active_rules = db.query(ComplianceRule).filter(ComplianceRule.is_active == True).all()
    rules_payload = [
        {
            "id": r.id,
            "rule_code": r.rule_code,
            "rule_name": r.rule_name,
            "required_documents": r.required_documents or [],
            "validation_conditions": r.validation_conditions or {}
        }
        for r in active_rules
    ]

    compliance_eval = ComplianceEngine.evaluate_compliance(
        application_data=app_data,
        institution_data=inst_data,
        uploaded_doc_types=uploaded_doc_types,
        active_rules=rules_payload,
        findings=created_findings,
        documents_with_extractions=docs_payload
    )

    for res in compliance_eval["results"]:
        comp_obj = ComplianceResult(
            application_id=app.id,
            rule_id=res["rule_id"],
            status=res["status"],
            score=res["score"],
            explanation=res["explanation"],
            evidence_summary=res.get("evidence_summary"),
            recommended_action=res.get("recommended_action")
        )
        db.add(comp_obj)

    # 3. Update Application Status & Risk Score
    app.compliance_score = compliance_eval["compliance_score"]
    app.risk_level = compliance_eval["risk_level"]
    
    warning_count = len([f for f in created_findings if f.get("severity") == "warning"])
    critical_count = len([f for f in created_findings if f.get("severity") == "critical"])
    
    if critical_count > 0:
        app.ai_validation_summary = f"CRITICAL: {critical_count} critical issues detected requiring immediate remediation."
    elif warning_count > 0:
        app.ai_validation_summary = f"WARNING: {warning_count} document inconsistencies flagged for officer review."
    else:
        app.ai_validation_summary = "AUTOMATED PASS: High entity consistency verified across submitted documentation."

    db.commit()


@router.get("/", response_model=List[ApplicationOut])
def list_applications(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Application)
    if current_user.role == "institution_admin":
        if current_user.institution_id:
            query = query.filter(Application.institution_id == current_user.institution_id)
        else:
            return []
    
    if status_filter:
        query = query.filter(Application.status == status_filter)

    return query.order_by(Application.created_at.desc()).all()


@router.get("/{application_id}", response_model=ApplicationDetailOut)
def get_application_details(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "institution_admin" and current_user.institution_id != app.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this application")

    return app


@router.post("/", response_model=ApplicationDetailOut)
def create_application(
    app_in: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.institution_id:
        # Create a default institution if institution_admin has none linked yet
        inst = Institution(
            name=f"{current_user.full_name}'s Institute",
            code=f"INST-{uuid.uuid4().hex[:6].upper()}",
            institution_type="Engineering & Technology",
            state="Delhi",
            district="New Delhi",
            address="Institutional Area, Sector 5",
            contact_email=current_user.email,
            contact_phone="+91-11-23456789"
        )
        db.add(inst)
        db.commit()
        db.refresh(inst)
        current_user.institution_id = inst.id
        db.commit()

    ref_id = f"AICTE-2026-{uuid.uuid4().hex[:6].upper()}"
    new_app = Application(
        reference_id=ref_id,
        institution_id=current_user.institution_id,
        academic_year=app_in.academic_year,
        status="draft",
        courses_offered=[c.dict() for c in app_in.courses_offered],
        student_intake=app_in.student_intake,
        faculty_count=app_in.faculty_count,
        campus_area_acres=app_in.campus_area_acres,
        built_up_area_sqm=app_in.built_up_area_sqm,
        compliance_score=0.0,
        risk_level="medium"
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    log_audit(db, action="APPLICATION_CREATED", resource_type="Application", resource_id=str(new_app.id), user_id=current_user.id)
    return new_app


@router.post("/{application_id}/submit")
def submit_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "institution_admin" and current_user.institution_id != app.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to submit this application")

    # Run AI pipeline
    execute_ai_validation_pipeline(app.id, db)
    
    app.status = "under_review"
    app.submitted_at = datetime.datetime.utcnow()
    db.commit()

    # Notify Officers
    officers = db.query(User).filter(User.role == "review_officer").all()
    for off in officers:
        db.add(Notification(
            user_id=off.id,
            title="New Application Submitted for Review",
            message=f"Application {app.reference_id} was submitted and processed through AI validation.",
            category="info",
            link=f"/officer/review/{app.id}"
        ))
    db.commit()

    log_audit(db, action="APPLICATION_SUBMITTED", resource_type="Application", resource_id=str(app.id), user_id=current_user.id)
    return {"message": "Application submitted successfully and processed through AI validation engine", "reference_id": app.reference_id}


@router.post("/{application_id}/re-audit")
def trigger_reaudit(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "institution_admin" and current_user.institution_id != app.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to trigger re-audit for this application")

    execute_ai_validation_pipeline(app.id, db)
    log_audit(db, action="AI_REAUDIT_TRIGGERED", resource_type="Application", resource_id=str(app.id), user_id=current_user.id)
    return {"message": "AI Document and Compliance verification pipeline re-executed successfully"}
