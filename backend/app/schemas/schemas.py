import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

# ----------------- Auth & Users -----------------
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "institution_admin"  # institution_admin, review_officer, system_admin
    institution_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    institution_id: Optional[int] = None
    is_active: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ----------------- Institutions -----------------
class InstitutionBase(BaseModel):
    name: str
    code: str
    institution_type: str = "Engineering & Technology"
    state: str
    district: str
    address: str
    contact_email: str
    contact_phone: str

class InstitutionCreate(InstitutionBase):
    pass

class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    institution_type: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class InstitutionOut(InstitutionBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Document Extractions -----------------
class DocumentExtractionOut(BaseModel):
    id: int
    document_id: int
    extracted_fields: Dict[str, Any]
    raw_text: Optional[str] = None
    ocr_method: str
    confidence_score: Optional[float] = None
    extraction_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Verification Findings -----------------
class VerificationFindingOut(BaseModel):
    id: int
    application_id: int
    document_id: Optional[int] = None
    finding_type: str
    title: str
    severity: str
    explanation: str
    recommended_action: str
    evidence_snippet: Optional[str] = None
    source_doc_title: Optional[str] = None
    page_number: Optional[int] = None
    is_resolved: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

# ----------------- Documents -----------------
class DocumentOut(BaseModel):
    id: int
    application_id: int
    document_type: str
    filename: str
    original_name: str
    file_path: str
    file_size: int
    mime_type: str
    verification_status: str
    verification_provider: str
    is_simulated: bool
    uploaded_at: datetime.datetime
    extraction: Optional[DocumentExtractionOut] = None
    findings: List[VerificationFindingOut] = []

    model_config = ConfigDict(from_attributes=True)

# ----------------- Compliance Rules & Results -----------------
class ComplianceRuleBase(BaseModel):
    rule_code: str
    rule_name: str
    description: str
    applicable_institution_type: str = "All"
    required_documents: List[str] = []
    validation_conditions: Dict[str, Any] = {}
    regulatory_source: str = "AICTE Approval Process Handbook (Synthetic Demo)"
    effective_date: str = "2026-01-01"
    rule_version: str = "v2026.1"
    is_active: bool = True

class ComplianceRuleCreate(ComplianceRuleBase):
    pass

class ComplianceRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    description: Optional[str] = None
    applicable_institution_type: Optional[str] = None
    required_documents: Optional[List[str]] = None
    validation_conditions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ComplianceRuleOut(ComplianceRuleBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class ComplianceResultOut(BaseModel):
    id: int
    application_id: int
    rule_id: int
    status: str
    score: float
    explanation: str
    evidence_summary: Optional[str] = None
    recommended_action: Optional[str] = None
    evaluated_at: datetime.datetime
    rule: Optional[ComplianceRuleOut] = None

    model_config = ConfigDict(from_attributes=True)

# ----------------- Review Decisions -----------------
class ReviewDecisionCreate(BaseModel):
    decision: str  # request_clarification, request_correction, mark_complete_approved, reject_application
    remarks: str
    clarification_query: Optional[str] = None

class ClarificationResponseCreate(BaseModel):
    clarification_response: str

class ReviewDecisionOut(BaseModel):
    id: int
    application_id: int
    officer_id: Optional[int] = None
    decision: str
    remarks: str
    clarification_query: Optional[str] = None
    clarification_response: Optional[str] = None
    is_clarification_resolved: bool
    decided_at: datetime.datetime
    officer: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)

# ----------------- Applications -----------------
class CourseItem(BaseModel):
    name: str
    intake: int

class ApplicationCreate(BaseModel):
    academic_year: str = "2026-2027"
    courses_offered: List[CourseItem] = []
    student_intake: int = 300
    faculty_count: int = 25
    campus_area_acres: float = 7.5
    built_up_area_sqm: float = 12500.0

class ApplicationUpdate(BaseModel):
    courses_offered: Optional[List[CourseItem]] = None
    student_intake: Optional[int] = None
    faculty_count: Optional[int] = None
    campus_area_acres: Optional[float] = None
    built_up_area_sqm: Optional[float] = None

class ApplicationOut(BaseModel):
    id: int
    reference_id: str
    institution_id: int
    academic_year: str
    status: str
    student_intake: int
    faculty_count: int
    campus_area_acres: float
    built_up_area_sqm: float
    compliance_score: float
    risk_level: str
    ai_validation_summary: Optional[str] = None
    submitted_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    institution: Optional[InstitutionOut] = None

    model_config = ConfigDict(from_attributes=True)

class ApplicationDetailOut(ApplicationOut):
    courses_offered: List[Dict[str, Any]] = []
    documents: List[DocumentOut] = []
    findings: List[VerificationFindingOut] = []
    compliance_results: List[ComplianceResultOut] = []
    decisions: List[ReviewDecisionOut] = []

    model_config = ConfigDict(from_attributes=True)

# ----------------- Notifications & Audit -----------------
class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    category: str
    is_read: bool
    link: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: str
    timestamp: datetime.datetime
    user: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)

# ----------------- Analytics Overview -----------------
class AnalyticsOverview(BaseModel):
    total_applications: int
    submitted_applications: int
    under_review_applications: int
    approved_applications: int
    clarification_requested_applications: int
    correction_requested_applications: int
    rejected_applications: int
    average_processing_time_hours: float
    common_findings: List[Dict[str, Any]]
    compliance_category_breakdown: List[Dict[str, Any]]
    applications_by_status: List[Dict[str, Any]]
