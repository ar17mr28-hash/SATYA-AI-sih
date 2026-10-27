from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import User, Application, ReviewDecision, Notification, Institution
from ..schemas.schemas import ReviewDecisionCreate, ReviewDecisionOut, ClarificationResponseCreate, ApplicationDetailOut
from ..services.auth import get_current_user, require_roles, log_audit

router = APIRouter(prefix="/reviews", tags=["Reviews & Officer Workflow"])

@router.get("/queue", response_model=List[ApplicationDetailOut])
def get_review_queue(
    status_filter: Optional[str] = None,
    risk_filter: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_roles(["review_officer", "system_admin"])),
    db: Session = Depends(get_db)
):
    query = db.query(Application).join(Institution, Application.institution_id == Institution.id)
    
    if status_filter:
        query = query.filter(Application.status == status_filter)
    if risk_filter:
        query = query.filter(Application.risk_level == risk_filter)
    if search:
        query = query.filter(
            (Institution.name.ilike(f"%{search}%")) |
            (Application.reference_id.ilike(f"%{search}%")) |
            (Institution.code.ilike(f"%{search}%"))
        )

    return query.order_by(Application.created_at.desc()).all()


@router.post("/{application_id}/decision", response_model=ReviewDecisionOut)
def record_officer_decision(
    application_id: int,
    decision_in: ReviewDecisionCreate,
    current_user: User = Depends(require_roles(["review_officer", "system_admin"])),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    decision_mapping = {
        "mark_complete_approved": "approved",
        "reject_application": "rejected",
        "request_clarification": "clarification_requested",
        "request_correction": "correction_requested"
    }
    new_status = decision_mapping.get(decision_in.decision)
    if not new_status:
        raise HTTPException(status_code=400, detail="Invalid decision value")

    app.status = new_status

    decision_record = ReviewDecision(
        application_id=app.id,
        officer_id=current_user.id,
        decision=decision_in.decision,
        remarks=decision_in.remarks,
        clarification_query=decision_in.clarification_query if decision_in.decision == "request_clarification" else None
    )
    db.add(decision_record)
    db.commit()
    db.refresh(decision_record)

    # Notify Institution Admins
    inst_users = db.query(User).filter(User.institution_id == app.institution_id).all()
    for u in inst_users:
        db.add(Notification(
            user_id=u.id,
            title=f"Application Status Updated: {new_status.replace('_', ' ').capitalize()}",
            message=f"Officer remarks: {decision_in.remarks}",
            category="action_required" if "requested" in new_status else ("success" if new_status == "approved" else "warning"),
            link=f"/applications/{app.id}"
        ))
    db.commit()

    log_audit(db, action="OFFICER_DECISION_RECORDED", resource_type="Application", resource_id=str(app.id), user_id=current_user.id, details={"decision": decision_in.decision, "remarks": decision_in.remarks})
    return decision_record


@router.post("/{application_id}/clarification-response")
def respond_to_clarification(
    application_id: int,
    response_in: ClarificationResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "institution_admin" and current_user.institution_id != app.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to respond to this application's query")

    latest_decision = db.query(ReviewDecision).filter(
        ReviewDecision.application_id == app.id,
        ReviewDecision.decision == "request_clarification"
    ).order_by(ReviewDecision.decided_at.desc()).first()

    if not latest_decision:
        raise HTTPException(status_code=400, detail="No active clarification request found for this application")

    latest_decision.clarification_response = response_in.clarification_response
    latest_decision.is_clarification_resolved = True
    app.status = "under_review"  # return to review queue
    db.commit()

    # Notify Officers
    officers = db.query(User).filter(User.role == "review_officer").all()
    for off in officers:
        db.add(Notification(
            user_id=off.id,
            title="Institution Responded to Clarification",
            message=f"Institution responded for application {app.reference_id}.",
            category="info",
            link=f"/officer/review/{app.id}"
        ))
    db.commit()

    log_audit(db, action="CLARIFICATION_RESPONSE_SUBMITTED", resource_type="Application", resource_id=str(app.id), user_id=current_user.id)
    return {"message": "Clarification response submitted successfully. Application returned to under review status."}
