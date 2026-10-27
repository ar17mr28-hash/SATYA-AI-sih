import pytest
from app.database.database import SessionLocal
from app.models.models import User, Application, Document, VerificationFinding, ComplianceRule
from app.schemas.schemas import UserLogin, ApplicationCreate, CourseItem, ReviewDecisionCreate
from app.api.auth import login
from app.api.applications import list_applications, get_application_details, create_application, submit_application
from app.api.compliance import get_compliance_rules
from app.api.analytics import get_analytics_overview
from app.api.reviews import record_officer_decision

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_officer_authentication(db):
    res = login(UserLogin(email="officer@aicte.gov.in", password="Officer@123"), db=db)
    assert "access_token" in res
    assert res["user"].role == "review_officer"

def test_demo_scenarios_exist(db):
    officer = db.query(User).filter(User.email == "officer@aicte.gov.in").first()
    apps = list_applications(current_user=officer, db=db)
    assert len(apps) >= 3

    # Check Scenario 1 (Apex: Low risk, 100% compliance)
    apex = next(a for a in apps if "APEX" in a.reference_id)
    assert apex.compliance_score == 100.0
    assert apex.risk_level == "low"

    # Check Scenario 2 (Bharati: High risk, missing doc)
    bharati = next(a for a in apps if "BHARATI" in a.reference_id)
    assert bharati.risk_level == "high"

    # Check Scenario 3 (Global: Medium risk, clarification requested)
    global_app = next(a for a in apps if "GLOBAL" in a.reference_id)
    assert global_app.risk_level == "medium"
    assert "clarification" in global_app.status

def test_explainable_ai_findings(db):
    officer = db.query(User).filter(User.email == "officer@aicte.gov.in").first()
    global_app = db.query(Application).filter(Application.reference_id.ilike("%GLOBAL%")).first()
    details = get_application_details(application_id=global_app.id, current_user=officer, db=db)
    
    assert len(details.findings) > 0
    mismatch = next(f for f in details.findings if "Mismatch" in f.title)
    assert mismatch.severity == "warning"
    assert "Global Technical Institute" in mismatch.explanation
    assert mismatch.evidence_snippet is not None

def test_compliance_rules(db):
    rules = get_compliance_rules(db=db)
    assert len(rules) >= 4
    rule_codes = [r.rule_code for r in rules]
    assert "RULE-MANDATORY-DOCS" in rule_codes
    assert "RULE-FACULTY-RATIO" in rule_codes
    assert "RULE-LAND-REQ" in rule_codes

def test_analytics_metrics(db):
    officer = db.query(User).filter(User.email == "officer@aicte.gov.in").first()
    analytics = get_analytics_overview(db=db, current_user=officer)
    assert analytics["total_applications"] >= 3
    assert len(analytics["status_distribution"]) > 0
    assert len(analytics["risk_distribution"]) > 0

def test_officer_review_decision(db):
    officer = db.query(User).filter(User.email == "officer@aicte.gov.in").first()
    global_app = db.query(Application).filter(Application.reference_id.ilike("%GLOBAL%")).first()
    
    dec = record_officer_decision(
        application_id=global_app.id,
        decision_in=ReviewDecisionCreate(
            decision="request_clarification",
            remarks="Please submit trust resolution matching institution name.",
            clarification_query="Please submit trust resolution matching institution name."
        ),
        current_user=officer,
        db=db
    )
    assert dec.decision == "request_clarification"
    assert dec.remarks == "Please submit trust resolution matching institution name."
