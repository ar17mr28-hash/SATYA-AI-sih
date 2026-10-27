import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import User, Application, Institution, Document, VerificationFinding, ComplianceResult, ReviewDecision
from ..services.auth import get_current_user, log_audit
from ..services.report_generator import ComplianceReportGenerator

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORT_DIR = os.path.join(os.getcwd(), "backend", "reports")

@router.get("/compliance/{application_id}")
def download_compliance_report(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "institution_admin" and current_user.institution_id != app.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to download this report")

    institution = db.query(Institution).filter(Institution.id == app.institution_id).first()
    documents = db.query(Document).filter(Document.application_id == app.id).all()
    findings = db.query(VerificationFinding).filter(VerificationFinding.application_id == app.id).all()
    compliance_results = db.query(ComplianceResult).filter(ComplianceResult.application_id == app.id).all()
    decisions = db.query(ReviewDecision).filter(ReviewDecision.application_id == app.id).all()

    # Prepare payload dictionaries
    app_data = {
        "id": app.id,
        "reference_id": app.reference_id,
        "academic_year": app.academic_year,
        "status": app.status,
        "compliance_score": app.compliance_score,
        "risk_level": app.risk_level,
        "submitted_at": app.submitted_at.strftime("%Y-%m-%d %H:%M") if app.submitted_at else "Draft"
    }

    inst_data = {
        "name": institution.name if institution else "N/A",
        "code": institution.code if institution else "N/A",
        "institution_type": institution.institution_type if institution else "N/A",
        "state": institution.state if institution else "N/A",
        "district": institution.district if institution else "N/A",
        "address": institution.address if institution else "N/A",
        "contact_email": institution.contact_email if institution else "N/A",
        "contact_phone": institution.contact_phone if institution else "N/A"
    }

    docs_list = []
    for d in documents:
        docs_list.append({
            "document_type": d.document_type,
            "filename": d.filename,
            "original_name": d.original_name,
            "verification_status": d.verification_status,
            "extraction": {
                "extracted_fields": d.extraction.extracted_fields if d.extraction else {},
                "ocr_method": d.extraction.ocr_method if d.extraction else "native_pdf",
                "confidence_score": d.extraction.confidence_score if d.extraction else None
            } if d.extraction else None
        })

    findings_list = [
        {
            "finding_type": f.finding_type,
            "title": f.title,
            "severity": f.severity,
            "explanation": f.explanation,
            "recommended_action": f.recommended_action,
            "evidence_snippet": f.evidence_snippet,
            "source_doc_title": f.source_doc_title
        }
        for f in findings
    ]

    comp_list = [
        {
            "status": c.status,
            "score": c.score,
            "explanation": c.explanation,
            "evidence_summary": c.evidence_summary,
            "rule": {
                "rule_code": c.rule.rule_code,
                "rule_name": c.rule.rule_name
            } if c.rule else {}
        }
        for c in compliance_results
    ]

    decisions_list = [
        {
            "decision": dec.decision,
            "remarks": dec.remarks,
            "officer": {"full_name": dec.officer.full_name} if dec.officer else None
        }
        for dec in decisions
    ]

    os.makedirs(REPORT_DIR, exist_ok=True)
    report_filename = f"VerifyAI_Compliance_Report_{app.reference_id}.pdf"
    output_path = os.path.join(REPORT_DIR, report_filename)

    ComplianceReportGenerator.generate_pdf_report(
        application_data=app_data,
        institution_data=inst_data,
        documents=docs_list,
        findings=findings_list,
        compliance_results=comp_list,
        decisions=decisions_list,
        output_path=output_path
    )

    log_audit(db, action="COMPLIANCE_REPORT_DOWNLOADED", resource_type="Application", resource_id=str(app.id), user_id=current_user.id)
    return FileResponse(
        path=output_path,
        filename=report_filename,
        media_type="application/pdf"
    )
