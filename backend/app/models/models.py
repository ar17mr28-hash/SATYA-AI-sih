import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from ..database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="institution_admin")  # institution_admin, review_officer, system_admin
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    institution = relationship("Institution", back_populates="users")
    decisions = relationship("ReviewDecision", back_populates="officer")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    institution_type = Column(String(100), default="Engineering & Technology")  # Engineering, Management, Pharmacy, Polytechnic
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    users = relationship("User", back_populates="institution")
    applications = relationship("Application", back_populates="institution", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String(100), unique=True, index=True, nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    academic_year = Column(String(20), default="2026-2027")
    status = Column(String(50), default="draft")  # draft, submitted, under_review, clarification_requested, correction_requested, approved, rejected
    
    # Institutional & Academic metrics
    courses_offered = Column(JSON, default=list)  # [{"name": "CSE", "intake": 120}]
    student_intake = Column(Integer, default=300)
    faculty_count = Column(Integer, default=25)
    campus_area_acres = Column(Float, default=7.5)
    built_up_area_sqm = Column(Float, default=12500.0)
    
    # AI Analysis & Assessment
    compliance_score = Column(Float, default=0.0)  # 0 to 100
    risk_level = Column(String(20), default="medium")  # low, medium, high
    ai_validation_summary = Column(Text, nullable=True)

    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    institution = relationship("Institution", back_populates="applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    findings = relationship("VerificationFinding", back_populates="application", cascade="all, delete-orphan")
    compliance_results = relationship("ComplianceResult", back_populates="application", cascade="all, delete-orphan")
    decisions = relationship("ReviewDecision", back_populates="application", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(100), nullable=False)  # Registration Certificate, Land Document, Faculty Qualification, Building Safety, AICTE Approval, Balance Sheet
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), default="application/pdf")
    # Separated State Model (OWASP / Defect 5.1)
    processing_status = Column(String(50), default="UPLOADED")  # UPLOADED, PROCESSING, PROCESSED, PROCESSING_FAILED
    authenticity_status = Column(String(50), default="NOT_CHECKED")  # NOT_CHECKED, CHECKS_PASSED, CHECKS_FAILED, REVIEW_REQUIRED, INCONCLUSIVE
    file_hash_sha256 = Column(String(64), nullable=True)  # Real cryptographic SHA-256 integrity hash
    authenticity_checks = Column(JSON, default=dict)  # Details of specific checks performed

    # Legacy / UI mapped fields
    verification_status = Column(String(50), default="requires_review")  # requires_review, not_authenticated, checks_passed, rejected
    verification_provider = Column(String(100), default="VerifyAI Pipeline (SHA-256 Integrity + Cross-Check)")
    is_simulated = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="documents")
    extraction = relationship("DocumentExtraction", back_populates="document", uselist=False, cascade="all, delete-orphan")
    findings = relationship("VerificationFinding", back_populates="document", cascade="all, delete-orphan")


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    extracted_fields = Column(JSON, default=dict)  # {"institution_name": "...", "issue_date": "...", etc.}
    raw_text = Column(Text, nullable=True)
    ocr_method = Column(String(50), default="native_pdf")  # native_pdf, tesseract_ocr, simulated
    confidence_score = Column(Float, nullable=True)  # None if unavailable
    extraction_metadata = Column(JSON, default=dict)  # page count, detected language, bounding boxes
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="extraction")


class VerificationFinding(Base):
    __tablename__ = "verification_findings"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    finding_type = Column(String(50), nullable=False)  # inconsistency, missing_field, missing_document, discrepancy
    title = Column(String(255), nullable=False)
    severity = Column(String(20), default="warning")  # info, warning, critical
    explanation = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    evidence_snippet = Column(Text, nullable=True)
    source_doc_title = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="findings")
    document = relationship("Document", back_populates="findings")


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(50), unique=True, index=True, nullable=False)
    rule_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    applicable_institution_type = Column(String(100), default="All")  # All, Engineering & Technology, Management, Polytechnic
    required_documents = Column(JSON, default=list)  # list of doc types required
    validation_conditions = Column(JSON, default=dict)  # e.g., {"min_faculty_ratio": 20, "min_campus_acres": 5.0}
    regulatory_source = Column(String(255), default="AICTE Approval Process Handbook (Synthetic Demonstration)")
    effective_date = Column(String(50), default="2026-01-01")
    rule_version = Column(String(20), default="v2026.1")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    compliance_results = relationship("ComplianceResult", back_populates="rule", cascade="all, delete-orphan")


class ComplianceResult(Base):
    __tablename__ = "compliance_results"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(Integer, ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)  # satisfied, not_satisfied, insufficient_evidence, requires_human_review
    score = Column(Float, default=1.0)  # 0.0 to 1.0
    explanation = Column(Text, nullable=False)
    evidence_summary = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="compliance_results")
    rule = relationship("ComplianceRule", back_populates="compliance_results")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    officer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decision = Column(String(50), nullable=False)  # request_clarification, request_correction, mark_complete_approved, reject_application
    remarks = Column(Text, nullable=False)
    clarification_query = Column(Text, nullable=True)
    clarification_response = Column(Text, nullable=True)
    is_clarification_resolved = Column(Boolean, default=False)
    decided_at = Column(DateTime, default=datetime.datetime.utcnow)

    application = relationship("Application", back_populates="decisions")
    officer = relationship("User", back_populates="decisions")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="info")  # info, warning, success, action_required
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., APPLICATION_SUBMITTED, DOCUMENT_UPLOADED, DECISION_RECORDED, RULE_MODIFIED
    resource_type = Column(String(100), nullable=False)  # Application, Document, ComplianceRule, User
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), default="127.0.0.1")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


class VerificationRun(Base):
    __tablename__ = "verification_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    query = Column(Text, nullable=True)
    response_text = Column(Text, nullable=False)
    overall_trust_score = Column(Float, default=0.0)
    faithfulness_score = Column(Float, default=0.0)
    grounding_coverage = Column(Float, default=0.0)
    contradiction_rate = Column(Float, default=0.0)
    risk_rating = Column(String(50), default="LOW_RISK")
    total_claims = Column(Integer, default=0)
    supported_count = Column(Integer, default=0)
    contradicted_count = Column(Integer, default=0)
    insufficient_count = Column(Integer, default=0)
    unverifiable_count = Column(Integer, default=0)
    claims_data = Column(JSON, default=list)
    scorecard_data = Column(JSON, default=dict)
    security_data = Column(JSON, default=dict)
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

