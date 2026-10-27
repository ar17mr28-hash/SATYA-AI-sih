import os
import datetime
from sqlalchemy.orm import Session
from ..database.database import engine, Base, SessionLocal
from ..models.models import (
    User, Institution, Application, Document, DocumentExtraction,
    VerificationFinding, ComplianceRule, ComplianceResult, ReviewDecision,
    Notification, AuditLog
)
from .auth import hash_password

def create_sample_pdf(file_path: str, title: str, content_lines: list):
    """
    Creates a real, clean PDF document using reportlab for demonstration files.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    doc = SimpleDocTemplate(file_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        'DocH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A")
    )
    body_style = ParagraphStyle(
        'DocB',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E293B")
    )

    story = [
        Paragraph(title, header_style),
        Spacer(1, 10)
    ]
    for line in content_lines:
        story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 6))

    doc.build(story)


def seed_database(db: Session = None):
    close_db = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_db = True

    try:
        # Check if already seeded
        existing_admin = db.query(User).filter(User.email == "sysadmin@aicte.gov.in").first()
        if existing_admin:
            print("Database already contains seed data.")
            return

        print("Seeding database with SIH 2026 VerifyAI demonstration dataset...")

        # 1. Institutions
        inst1 = Institution(
            name="Apex Institute of Technology & Engineering",
            code="APEX-ENG-101",
            institution_type="Engineering & Technology",
            state="Maharashtra",
            district="Pune",
            address="Plot 42, Hinjawadi Phase 2, Pune, Maharashtra 411057",
            contact_email="principal@apexinstitute.ac.in",
            contact_phone="+91-20-88997701"
        )
        inst2 = Institution(
            name="Bharati Academy of Technical Studies",
            code="BHARATI-TEC-202",
            institution_type="Polytechnic & Diploma",
            state="Karnataka",
            district="Bengaluru Urban",
            address="Campus 9, Electronic City Phase 1, Bengaluru, Karnataka 560100",
            contact_email="admin@bharatiu.ac.in",
            contact_phone="+91-80-45678901"
        )
        inst3 = Institution(
            name="Global Institute of Technology",
            code="GLOBAL-ENG-303",
            institution_type="Engineering & Technology",
            state="Tamil Nadu",
            district="Chennai",
            address="104, Old Mahabalipuram Road, Chennai, Tamil Nadu 600096",
            contact_email="registrar@globaltech.edu.in",
            contact_phone="+91-44-24567890"
        )
        db.add_all([inst1, inst2, inst3])
        db.commit()
        db.refresh(inst1)
        db.refresh(inst2)
        db.refresh(inst3)

        # 2. Users (Documented Demo Accounts)
        users = [
            User(
                email="sysadmin@aicte.gov.in",
                hashed_password=hash_password("SysAdmin@123"),
                full_name="Rajesh Sharma (System Admin)",
                role="system_admin",
                is_active=True
            ),
            User(
                email="officer@aicte.gov.in",
                hashed_password=hash_password("Officer@123"),
                full_name="Dr. Sunita Kulkarni (Review Officer)",
                role="review_officer",
                is_active=True
            ),
            User(
                email="institution@verifyai.gov.in",
                hashed_password=hash_password("Admin@123"),
                full_name="Prof. Anand Verma (Apex Admin)",
                role="institution_admin",
                institution_id=inst1.id,
                is_active=True
            ),
            User(
                email="bharati@verifyai.gov.in",
                hashed_password=hash_password("Bharati@123"),
                full_name="Dr. Ramesh Rao (Bharati Admin)",
                role="institution_admin",
                institution_id=inst2.id,
                is_active=True
            ),
            User(
                email="global@verifyai.gov.in",
                hashed_password=hash_password("Global@123"),
                full_name="Dr. V. Ramanathan (Global Admin)",
                role="institution_admin",
                institution_id=inst3.id,
                is_active=True
            )
        ]
        db.add_all(users)
        db.commit()

        # 3. Regulatory Compliance Rules
        rules = [
            ComplianceRule(
                rule_code="RULE-MANDATORY-DOCS",
                rule_name="Mandatory Statutory Documents Verification",
                description="Institution must submit Registration Certificate, Land Deed, Building Safety NOC, and Faculty List.",
                applicable_institution_type="All",
                required_documents=["Registration Certificate", "Land Document", "Building Safety", "Faculty Qualification"],
                validation_conditions={"mandatory_all_present": True},
                regulatory_source="AICTE APH Section 2.3 (Synthetic Demo Rule)",
                effective_date="2026-01-01",
                rule_version="v2026.1"
            ),
            ComplianceRule(
                rule_code="RULE-FACULTY-RATIO",
                rule_name="Cadre & Student-to-Faculty Ratio (SFR)",
                description="Technical institutions must maintain an overall student-to-faculty ratio not exceeding 1:20.",
                applicable_institution_type="Engineering & Technology",
                required_documents=["Faculty Qualification"],
                validation_conditions={"max_student_faculty_ratio": 20.0},
                regulatory_source="AICTE Norms for Technical Programs (Synthetic Demo Rule)",
                effective_date="2026-01-01",
                rule_version="v2026.1"
            ),
            ComplianceRule(
                rule_code="RULE-LAND-REQ",
                rule_name="Minimum Contiguous Campus Land Area",
                description="Engineering colleges require a minimum contiguous land parcel of 5.0 Acres in non-metro regions.",
                applicable_institution_type="Engineering & Technology",
                required_documents=["Land Document"],
                validation_conditions={"min_campus_acres": 5.0},
                regulatory_source="AICTE Land & Building Norms Table 4.1 (Synthetic Demo)",
                effective_date="2026-01-01",
                rule_version="v2026.1"
            ),
            ComplianceRule(
                rule_code="RULE-BUILTUP-AREA",
                rule_name="Instructional & Administrative Built-up Area",
                description="Total approved built-up infrastructure must measure at least 10,000 square meters.",
                applicable_institution_type="Engineering & Technology",
                required_documents=["Building Safety"],
                validation_conditions={"min_built_up_sqm": 10000.0},
                regulatory_source="AICTE Infrastructure Guidelines (Synthetic Demo)",
                effective_date="2026-01-01",
                rule_version="v2026.1"
            ),
            ComplianceRule(
                rule_code="RULE-FIRE-SAFETY",
                rule_name="Valid Fire Safety & Occupancy Certificate",
                description="Institution must possess a valid, non-expired Fire Safety NOC from the Fire Services Authority.",
                applicable_institution_type="All",
                required_documents=["Building Safety"],
                validation_conditions={"requires_valid_noc": True},
                regulatory_source="National Building Code & Fire Safety Act (Synthetic Demo)",
                effective_date="2026-01-01",
                rule_version="v2026.1"
            )
        ]
        db.add_all(rules)
        db.commit()

        # 4. Prepare Uploads Directory and Demo PDFs
        upload_base = os.path.join(os.getcwd(), "backend", "uploads")
        os.makedirs(upload_base, exist_ok=True)

        # ---------------- SCENARIO 1: Valid Application ----------------
        app1 = Application(
            reference_id="AICTE-2026-APEX-8821",
            institution_id=inst1.id,
            academic_year="2026-2027",
            status="approved",
            courses_offered=[
                {"name": "Computer Science & Engineering", "intake": 120},
                {"name": "Electronics & Telecommunication", "intake": 60},
                {"name": "Artificial Intelligence & Data Science", "intake": 60}
            ],
            student_intake=240,
            faculty_count=18,
            campus_area_acres=8.5,
            built_up_area_sqm=14200.0,
            compliance_score=100.0,
            risk_level="low",
            ai_validation_summary="All 4 mandatory documents verified. Cross-document entity consistency verified. All compliance rules satisfied.",
            submitted_at=datetime.datetime.utcnow() - datetime.timedelta(days=5)
        )
        db.add(app1)
        db.commit()
        db.refresh(app1)

        # Docs for App 1
        d1_path = os.path.join(upload_base, "apex_registration.pdf")
        create_sample_pdf(d1_path, "GOVERNMENT OF MAHARASHTRA - REGISTRAR OF SOCIETIES", [
            "Certificate of Registration",
            "Registration No: REG/MH/PUN/2012/8492",
            "This is to certify that Apex Institute of Technology & Engineering is duly registered under the Societies Registration Act XXI of 1860.",
            "Issued on: 15/06/2012 | Validity: Perpetual",
            "Issuing Authority: Registrar of Societies, Pune Division"
        ])
        doc1 = Document(
            application_id=app1.id,
            document_type="Registration Certificate",
            filename="apex_registration.pdf",
            original_name="Society_Registration_Certificate.pdf",
            file_path=d1_path,
            file_size=os.path.getsize(d1_path),
            verification_status="verified",
            is_simulated=True
        )
        db.add(doc1)
        db.commit()
        db.refresh(doc1)

        db.add(DocumentExtraction(
            document_id=doc1.id,
            extracted_fields={
                "institution_name": "Apex Institute of Technology & Engineering",
                "document_number": "REG/MH/PUN/2012/8492",
                "issue_date": "15/06/2012",
                "expiry_date": "Perpetual",
                "issuing_authority": "Registrar of Societies"
            },
            raw_text="Apex Institute of Technology & Engineering Registration Certificate REG/MH/PUN/2012/8492",
            ocr_method="native_pdf",
            confidence_score=0.96
        ))

        d2_path = os.path.join(upload_base, "apex_land_deed.pdf")
        create_sample_pdf(d2_path, "DEPARTMENT OF REVENUE & REGISTRATION - LAND TITLE DEED", [
            "Registered Land Conveyance Deed",
            "Document Number: DEED/PUN/HINJ/4401",
            "Name of Institution: Apex Institute of Technology & Engineering",
            "Total Land Area: 8.5 Acres (Contiguous parcel)",
            "Issued on: 10/08/2014 | Issuing Authority: Sub-Registrar Office, Mulshi Pune"
        ])
        doc2 = Document(
            application_id=app1.id,
            document_type="Land Document",
            filename="apex_land_deed.pdf",
            original_name="Registered_Land_Title_Deed.pdf",
            file_path=d2_path,
            file_size=os.path.getsize(d2_path),
            verification_status="verified",
            is_simulated=True
        )
        db.add(doc2)
        db.commit()
        db.refresh(doc2)

        db.add(DocumentExtraction(
            document_id=doc2.id,
            extracted_fields={
                "institution_name": "Apex Institute of Technology & Engineering",
                "document_number": "DEED/PUN/HINJ/4401",
                "land_area_acres": 8.5,
                "issuing_authority": "Sub-Registrar Office"
            },
            raw_text="Land title deed 8.5 Acres Apex Institute of Technology & Engineering",
            ocr_method="native_pdf",
            confidence_score=0.95
        ))

        d3_path = os.path.join(upload_base, "apex_fire_noc.pdf")
        create_sample_pdf(d3_path, "MAHARASHTRA FIRE SERVICES - FIRE SAFETY NO OBJECTION CERTIFICATE", [
            "Building Fire Safety & Fitness NOC",
            "Document No: NOC/FIRE/PUN/2025/1102",
            "Name of Institution: Apex Institute of Technology & Engineering",
            "Total Built-up Area: 14200 sqm",
            "Issued on: 05/01/2025 | Valid Upto: 04/01/2028",
            "Issuing Authority: Fire and Emergency Services Department"
        ])
        doc3 = Document(
            application_id=app1.id,
            document_type="Building Safety",
            filename="apex_fire_noc.pdf",
            original_name="Fire_Safety_NOC.pdf",
            file_path=d3_path,
            file_size=os.path.getsize(d3_path),
            verification_status="verified",
            is_simulated=True
        )
        db.add(doc3)
        db.commit()
        db.refresh(doc3)

        db.add(DocumentExtraction(
            document_id=doc3.id,
            extracted_fields={
                "institution_name": "Apex Institute of Technology & Engineering",
                "document_number": "NOC/FIRE/PUN/2025/1102",
                "issue_date": "05/01/2025",
                "expiry_date": "04/01/2028",
                "issuing_authority": "Fire and Emergency Services Department"
            },
            raw_text="Fire Safety NOC Apex Institute of Technology & Engineering 14200 sqm",
            ocr_method="native_pdf",
            confidence_score=0.94
        ))

        # Add Compliance Results for App 1
        for rule in db.query(ComplianceRule).all():
            db.add(ComplianceResult(
                application_id=app1.id,
                rule_id=rule.id,
                status="satisfied",
                score=1.0,
                explanation=f"All requirements for {rule.rule_name} fully verified from submitted records.",
                evidence_summary="Documents verified with high confidence.",
                recommended_action="No action required."
            ))

        db.add(ReviewDecision(
            application_id=app1.id,
            officer_id=users[1].id,
            decision="mark_complete_approved",
            remarks="Full compliance verified. AI cross-document audit confirmed 100% entity consistency. Recommended for Extension of Approval.",
            decided_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        ))

        # ---------------- SCENARIO 2: Missing Required Document ----------------
        app2 = Application(
            reference_id="AICTE-2026-BHARATI-4419",
            institution_id=inst2.id,
            academic_year="2026-2027",
            status="correction_requested",
            courses_offered=[
                {"name": "Diploma in Mechanical Engineering", "intake": 60},
                {"name": "Diploma in Electrical & Electronics", "intake": 60}
            ],
            student_intake=120,
            faculty_count=7,
            campus_area_acres=4.0,
            built_up_area_sqm=7500.0,
            compliance_score=40.0,
            risk_level="high",
            ai_validation_summary="CRITICAL: Missing mandatory Land Title Deed. Campus land area and building safety requirements cannot be satisfied without statutory proof.",
            submitted_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
        )
        db.add(app2)
        db.commit()
        db.refresh(app2)

        d4_path = os.path.join(upload_base, "bharati_registration.pdf")
        create_sample_pdf(d4_path, "GOVERNMENT OF KARNATAKA - REGISTRAR OF SOCIETIES", [
            "Society Registration Certificate",
            "Registration No: REG/KA/BNG/2018/3310",
            "Name of Institution: Bharati Academy of Technical Studies",
            "Issued on: 12/03/2018 | Validity: Perpetual"
        ])
        doc4 = Document(
            application_id=app2.id,
            document_type="Registration Certificate",
            filename="bharati_registration.pdf",
            original_name="Bharati_Society_Registration.pdf",
            file_path=d4_path,
            file_size=os.path.getsize(d4_path),
            verification_status="verified",
            is_simulated=True
        )
        db.add(doc4)
        db.commit()
        db.refresh(doc4)

        db.add(DocumentExtraction(
            document_id=doc4.id,
            extracted_fields={
                "institution_name": "Bharati Academy of Technical Studies",
                "document_number": "REG/KA/BNG/2018/3310"
            },
            raw_text="Bharati Academy of Technical Studies Society Registration",
            ocr_method="native_pdf",
            confidence_score=0.95
        ))

        # Add Finding for App 2
        db.add(VerificationFinding(
            application_id=app2.id,
            finding_type="missing_document",
            title="Mandatory Land Title Deed Document Missing",
            severity="critical",
            explanation="The application did not include a Land Ownership Title Deed or Registered Lease Document.",
            recommended_action="Institution must immediately upload registered land ownership records.",
            evidence_snippet="Missing from Document Submission Checklist: [Land Document]",
            source_doc_title="Application Manifest",
            page_number=1
        ))

        # Results for App 2
        for rule in db.query(ComplianceRule).all():
            if "LAND" in rule.rule_code or "MANDATORY" in rule.rule_code:
                db.add(ComplianceResult(
                    application_id=app2.id,
                    rule_id=rule.id,
                    status="not_satisfied",
                    score=0.0,
                    explanation=f"Missing mandatory Land Document required under {rule.rule_name}.",
                    evidence_summary="Land Title Deed was omitted from submission.",
                    recommended_action="Submit registered Land Title Deed."
                ))
            else:
                db.add(ComplianceResult(
                    application_id=app2.id,
                    rule_id=rule.id,
                    status="satisfied",
                    score=1.0,
                    explanation=f"Evaluated criteria met.",
                    evidence_summary="Criteria satisfied.",
                    recommended_action="None"
                ))

        db.add(ReviewDecision(
            application_id=app2.id,
            officer_id=users[1].id,
            decision="request_correction",
            remarks="Application rejected in preliminary automated filter due to missing land title documentation. Please re-upload.",
            decided_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
        ))

        # ---------------- SCENARIO 3: Institution Name Mismatch ----------------
        app3 = Application(
            reference_id="AICTE-2026-GLOBAL-7730",
            institution_id=inst3.id,
            academic_year="2026-2027",
            status="clarification_requested",
            courses_offered=[
                {"name": "Computer Science & Engineering", "intake": 180},
                {"name": "Information Technology", "intake": 60}
            ],
            student_intake=240,
            faculty_count=15,
            campus_area_acres=6.0,
            built_up_area_sqm=11000.0,
            compliance_score=80.0,
            risk_level="medium",
            ai_validation_summary="WARNING: Detected name discrepancy between Application ('Global Institute of Technology') and Registration Document ('Global Technical Institute'). Human clarification required.",
            submitted_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
        )
        db.add(app3)
        db.commit()
        db.refresh(app3)

        d5_path = os.path.join(upload_base, "global_mismatched_registration.pdf")
        create_sample_pdf(d5_path, "GOVERNMENT OF TAMIL NADU - REGISTRAR OF SOCIETIES", [
            "Certificate of Society Incorporation",
            "Registration No: REG/TN/CHN/2015/6612",
            "This is to certify that Global Technical Institute is registered under Society Registration Act.",
            "Issued on: 22/07/2015 | Issuing Authority: Registrar of Societies, Chennai South"
        ])
        doc5 = Document(
            application_id=app3.id,
            document_type="Registration Certificate",
            filename="global_mismatched_registration.pdf",
            original_name="Society_Registration_Certificate.pdf",
            file_path=d5_path,
            file_size=os.path.getsize(d5_path),
            verification_status="requires_review",
            is_simulated=True
        )
        db.add(doc5)
        db.commit()
        db.refresh(doc5)

        db.add(DocumentExtraction(
            document_id=doc5.id,
            extracted_fields={
                "institution_name": "Global Technical Institute",
                "document_number": "REG/TN/CHN/2015/6612",
                "issue_date": "22/07/2015",
                "issuing_authority": "Registrar of Societies"
            },
            raw_text="Global Technical Institute Certificate of Society Incorporation REG/TN/CHN/2015/6612",
            ocr_method="native_pdf",
            confidence_score=0.93
        ))

        d6_path = os.path.join(upload_base, "global_land_deed.pdf")
        create_sample_pdf(d6_path, "SUB-REGISTRAR OFFICE - CONVEYANCE DEED", [
            "Title Deed for Educational Campus",
            "Document Number: DEED/TN/CHN/9920",
            "Name of Institution: Global Institute of Technology",
            "Total Land Area: 6.0 Acres",
            "Issued on: 18/09/2016"
        ])
        doc6 = Document(
            application_id=app3.id,
            document_type="Land Document",
            filename="global_land_deed.pdf",
            original_name="Land_Title_Deed_6Acres.pdf",
            file_path=d6_path,
            file_size=os.path.getsize(d6_path),
            verification_status="verified",
            is_simulated=True
        )
        db.add(doc6)
        db.commit()
        db.refresh(doc6)

        db.add(DocumentExtraction(
            document_id=doc6.id,
            extracted_fields={
                "institution_name": "Global Institute of Technology",
                "document_number": "DEED/TN/CHN/9920",
                "land_area_acres": 6.0
            },
            raw_text="Global Institute of Technology Land Title Deed 6.0 Acres",
            ocr_method="native_pdf",
            confidence_score=0.96
        ))

        # Add Explainable Finding for App 3
        db.add(VerificationFinding(
            application_id=app3.id,
            document_id=doc5.id,
            finding_type="inconsistency",
            title="Institution Name Mismatch in Registration Certificate",
            severity="warning",
            explanation=(
                "The institution name stated in the application ('Global Institute of Technology') "
                "differs from the legal entity name extracted from Registration Certificate ('Global Technical Institute') "
                "with an entity token match of 64%."
            ),
            recommended_action=(
                "Request formal clarification or government resolution document regarding the trade name vs registered society name. "
                "Do not automatically reject or declare fraudulent."
            ),
            evidence_snippet="Extracted: \"Global Technical Institute\" vs Application: \"Global Institute of Technology\"",
            source_doc_title="Registration Certificate (global_mismatched_registration.pdf)",
            page_number=1
        ))

        for rule in db.query(ComplianceRule).all():
            if "MANDATORY" in rule.rule_code:
                db.add(ComplianceResult(
                    application_id=app3.id,
                    rule_id=rule.id,
                    status="requires_human_review",
                    score=0.70,
                    explanation="Mandatory documents attached, but an entity name discrepancy was detected in the Registration Certificate.",
                    evidence_summary="Extracted name discrepancy flagged.",
                    recommended_action="Officer should verify name change resolution."
                ))
            else:
                db.add(ComplianceResult(
                    application_id=app3.id,
                    rule_id=rule.id,
                    status="satisfied",
                    score=1.0,
                    explanation=f"Requirements for {rule.rule_name} satisfied.",
                    evidence_summary="Criteria satisfied.",
                    recommended_action="None"
                ))

        db.add(ReviewDecision(
            application_id=app3.id,
            officer_id=users[1].id,
            decision="request_clarification",
            remarks="Please provide official notification or governing body resolution explaining the difference between 'Global Technical Institute' on your registration certificate and 'Global Institute of Technology' in your application.",
            clarification_query="Please provide official notification or governing body resolution explaining the difference between 'Global Technical Institute' on your registration certificate and 'Global Institute of Technology' in your application.",
            decided_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        ))

        # 5. Notifications
        db.add(Notification(
            user_id=users[2].id,
            title="Application Approved",
            message="Your institutional application AICTE-2026-APEX-8821 has been marked complete and approved.",
            category="success",
            link="/applications"
        ))
        db.add(Notification(
            user_id=users[4].id,
            title="Clarification Requested by AICTE Officer",
            message="Officer Dr. Sunita Kulkarni requested clarification regarding your institution name on Registration Certificate.",
            category="warning",
            link="/applications"
        ))
        db.add(Notification(
            user_id=users[1].id,
            title="New Applications In Scrutiny Queue",
            message="3 applications submitted for AICTE regulatory verification cycle 2026-2027.",
            category="info",
            link="/officer"
        ))

        # 6. Audit Logs
        db.add(AuditLog(
            user_id=users[0].id,
            action="SYSTEM_INIT_SEED",
            resource_type="System",
            resource_id="INITIAL_BOOT",
            details={"demo_scenarios_loaded": ["Scenario 1: Valid", "Scenario 2: Missing Doc", "Scenario 3: Name Mismatch"]}
        ))

        db.commit()
        print("Database successfully seeded with 3 demo scenarios and all roles!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    seed_database()
