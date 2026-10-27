from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db, Base, engine
from ..models.models import (
    User, Institution, Application, Document, DocumentExtraction,
    VerificationFinding, ComplianceRule, ComplianceResult, ReviewDecision,
    Notification, AuditLog
)
from ..services.seed import seed_database
from ..services.auth import get_current_user

router = APIRouter(prefix="/demo", tags=["Demo Mode & Judges Scenarios"])

SCENARIOS = [
    {
        "id": "scenario-1",
        "title": "Scenario 1: Fully Valid Application",
        "institution": "Apex Institute of Technology & Engineering",
        "reference_id": "AICTE-2026-APEX-8821",
        "description": "Application with all mandatory documents attached. Full cross-document entity consistency verified. All AICTE regulatory rules satisfied (100% compliance score).",
        "expected_result": "Automated verification pass, zero discrepancies, Low risk profile, approved status."
    },
    {
        "id": "scenario-2",
        "title": "Scenario 2: Missing Mandatory Document",
        "institution": "Bharati Academy of Technical Studies",
        "reference_id": "AICTE-2026-BHARATI-4419",
        "description": "Institution omitted the mandatory Registered Land Title Deed from submission.",
        "expected_result": "System identifies missing statutory document, flags critical finding, sets compliance score to 40% with High risk, and triggers correction workflow."
    },
    {
        "id": "scenario-3",
        "title": "Scenario 3: Cross-Document Name Inconsistency",
        "institution": "Global Institute of Technology",
        "reference_id": "AICTE-2026-GLOBAL-7730",
        "description": "Application form lists 'Global Institute of Technology', while Registration Certificate contains 'Global Technical Institute'.",
        "expected_result": "Explainable AI flags name mismatch (64% match) with verbatim text evidence. Instead of false fraud accusation, system triggers human clarification request."
    }
]

@router.get("/scenarios")
def get_demo_scenarios():
    return {
        "status": "active",
        "mode": "SIH 2026 Evaluation Demonstration Mode",
        "scenarios": SCENARIOS
    }

@router.post("/reset")
def reset_demo_database(db: Session = Depends(get_db)):
    """
    Clears all tables and re-executes seed_database to reset demo state for judges.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_database(db)
    return {
        "message": "VerifyAI database reset successfully to pristine SIH demonstration state with all 3 scenarios pre-loaded.",
        "scenarios": SCENARIOS
    }
