import os
import io
import pytest
from fastapi import HTTPException, UploadFile
from app.database.database import SessionLocal
from app.models.models import User, Application, Document, ComplianceResult
from app.schemas.schemas import UserRegister
from app.api.auth import register
from app.api.applications import get_application_details, trigger_reaudit
from app.api.documents import upload_document
from app.services.auth import validate_production_security_config

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_production_security_config_rejection():
    """Verify that starting in production with a weak or default JWT key raises RuntimeError."""
    orig_env = os.environ.get("ENVIRONMENT")
    orig_key = os.environ.get("SECRET_KEY")
    try:
        os.environ["ENVIRONMENT"] = "production"
        os.environ["SECRET_KEY"] = "short_key"
        with pytest.raises(RuntimeError) as exc_info:
            validate_production_security_config()
        assert "CRITICAL SECURITY CONFIGURATION ERROR" in str(exc_info.value)

        # Test empty key
        os.environ["SECRET_KEY"] = ""
        with pytest.raises(RuntimeError) as exc_info:
            validate_production_security_config()
        assert "CRITICAL SECURITY CONFIGURATION ERROR" in str(exc_info.value)
    finally:
        if orig_env is not None:
            os.environ["ENVIRONMENT"] = orig_env
        else:
            os.environ.pop("ENVIRONMENT", None)
        if orig_key is not None:
            os.environ["SECRET_KEY"] = orig_key
        else:
            os.environ.pop("SECRET_KEY", None)

def test_public_registration_blocks_privilege_escalation(db):
    """Verify that public registration rejects attempts to self-provision privileged roles."""
    with pytest.raises(HTTPException) as exc_officer:
        register(
            UserRegister(
                email="attacker_officer@test.com",
                password="Password@123",
                full_name="Attacker",
                role="review_officer"
            ),
            db=db
        )
    assert exc_officer.value.status_code == 403
    assert "Privilege escalation prohibited" in exc_officer.value.detail

    with pytest.raises(HTTPException) as exc_admin:
        register(
            UserRegister(
                email="attacker_admin@test.com",
                password="Password@123",
                full_name="Attacker Admin",
                role="system_admin"
            ),
            db=db
        )
    assert exc_admin.value.status_code == 403
    assert "Privilege escalation prohibited" in exc_admin.value.detail

def test_idor_cross_institution_isolation(db):
    """Verify that institution A cannot view or re-audit institution B's application."""
    apex_user = db.query(User).filter(User.email == "institution@verifyai.gov.in").first()
    bharati_app = db.query(Application).filter(Application.reference_id.ilike("%BHARATI%")).first()

    assert apex_user is not None
    assert bharati_app is not None
    assert apex_user.institution_id != bharati_app.institution_id

    # 1. Test get_application_details IDOR protection
    with pytest.raises(HTTPException) as exc_view:
        get_application_details(application_id=bharati_app.id, current_user=apex_user, db=db)
    assert exc_view.value.status_code == 403
    assert "Not authorized" in exc_view.value.detail

    # 2. Test trigger_reaudit IDOR protection
    with pytest.raises(HTTPException) as exc_audit:
        trigger_reaudit(application_id=bharati_app.id, current_user=apex_user, db=db)
    assert exc_audit.value.status_code == 403
    assert "Not authorized" in exc_audit.value.detail

@pytest.mark.anyio
async def test_magic_byte_file_signature_validation(db):
    """Verify that files with spoofed extensions (e.g. text/exe pretending to be PDF) are rejected."""
    apex_user = db.query(User).filter(User.email == "institution@verifyai.gov.in").first()
    apex_app = db.query(Application).filter(Application.reference_id.ilike("%APEX%")).first()

    # Upload fake PDF containing non-PDF bytes
    fake_content = b"This is just plain text, not a PDF document header."
    fake_file = UploadFile(
        file=io.BytesIO(fake_content),
        filename="fake_document.pdf",
        headers={"content-type": "application/pdf"}
    )

    with pytest.raises(HTTPException) as exc_info:
        await upload_document(
            application_id=apex_app.id,
            document_type="Building Safety",
            file=fake_file,
            current_user=apex_user,
            db=db
        )
    assert exc_info.value.status_code == 400
    assert "File signature mismatch" in exc_info.value.detail

@pytest.mark.anyio
async def test_genuine_upload_truthful_state_model(db):
    """Verify that a valid PDF upload gets truthful status: NOT_CHECKED authenticity and not simulated."""
    apex_user = db.query(User).filter(User.email == "institution@verifyai.gov.in").first()
    apex_app = db.query(Application).filter(Application.reference_id.ilike("%APEX%")).first()

    # Valid PDF with standard %PDF- header
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n100\n%%EOF"
    valid_file = UploadFile(
        file=io.BytesIO(pdf_content),
        filename="valid_test_document.pdf",
        headers={"content-type": "application/pdf"}
    )

    doc = await upload_document(
        application_id=apex_app.id,
        document_type="Building Safety",
        file=valid_file,
        current_user=apex_user,
        db=db
    )

    assert doc.authenticity_status == "NOT_CHECKED"
    assert doc.is_simulated is False
    assert doc.file_hash_sha256 is not None
    assert len(doc.file_hash_sha256) == 64
    assert doc.authenticity_checks.get("magic_byte_verified") is True

    # Clean up uploaded test doc from DB
    db_doc = db.query(Document).filter(Document.id == doc.id).first()
    if db_doc:
        if os.path.exists(db_doc.file_path):
            try:
                os.remove(db_doc.file_path)
            except Exception:
                pass
        db.delete(db_doc)
        db.commit()

def test_scenario_d_unreadable_scan_truthful_reporting(db):
    """Verify that Scenario D (Zenith) reports insufficient_evidence rather than fabricating a pass."""
    zenith_app = db.query(Application).filter(Application.reference_id.ilike("%ZENITH%")).first()
    assert zenith_app is not None

    # Check that document authenticity is INCONCLUSIVE
    zenith_doc = db.query(Document).filter(Document.application_id == zenith_app.id).first()
    assert zenith_doc is not None
    assert zenith_doc.authenticity_status == "INCONCLUSIVE"
    assert zenith_doc.is_simulated is False

    # Check compliance results contain insufficient_evidence
    comp_results = db.query(ComplianceResult).filter(ComplianceResult.application_id == zenith_app.id).all()
    statuses = [c.status for c in comp_results]
    assert "insufficient_evidence" in statuses
    # Score should reflect low compliance, never 100%
    assert zenith_app.compliance_score <= 40.0
