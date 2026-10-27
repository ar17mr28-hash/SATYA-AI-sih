# VerifyAI Architecture & Technical Specifications
**Smart India Hackathon 2026** | **Problem Statement:** SIH26261  
**Organization:** All India Council for Technical Education (AICTE)

---

## 1. Executive Architecture Summary

VerifyAI is built upon a decoupled, high-performance full-stack architecture tailored to government scrutiny workflows:

1. **Frontend Presentation Layer (`/frontend`):**
   - React 18 with TypeScript and Vite.
   - Tailwind CSS with an authoritative government-enterprise color identity: Navy Blue (`#0F172A`), Royal Blue (`#2563EB`), Cyan (`#06B6D4`), Emerald Green (`#10B981`), Amber (`#F59E0B`), and Slate Gray (`#F8FAFC`).
   - Role-Based dashboards for **Institution Admins**, **AICTE Review Officers**, and **System Admins**.
   - Interactive judge demonstration bar with 1-click access to all 3 evaluated SIH scenarios.

2. **Backend Processing Layer (`/backend`):**
   - Python 3.13 with FastAPI and async routing.
   - Pydantic V2 data validation and strict typing.
   - SQLAlchemy ORM with SQLite local fallback and PostgreSQL support.
   - Secure cryptographic password hashing via BCrypt and stateless JWT session handling.

3. **AI Document Intelligence Engine (`/backend/app/ai`):**
   - **Parser:** PyMuPDF (`pymupdf`) for native vector PDF text extraction and structure extraction; Pillow for raster image processing.
   - **Classifier:** Keyword-frequency and structural heuristic classifier identifying Registration Certificates, Land Deeds, Building Safety NOCs, Faculty Lists, and Financials.
   - **Extractor:** Regular expression entity extractor parsing Institution Names, Document/Registration Codes, Issue Dates, Expiry Dates, Campus Acreage, and Built-Up Area.
   - **Consistency Engine:** Multi-factor entity matching combining Jaccard token overlap and SequenceMatcher string distance to detect name discrepancies without false fraud accusations.
   - **Explainable AI (XAI) Engine:** Synthesizes human-readable audit explanations citing verbatim extracted document text, source document name, page number, and remedial action.
   - **Regulatory Compliance Engine:** Compares institutional metrics against configurable AICTE Approval Process Handbook (APH) rules.

4. **Official PDF Compliance Report Engine (`/backend/app/services/report_generator.py`):**
   - ReportLab flowable engine rendering government-grade multi-page audit reports with digital seals, SHA-256 integrity hashes, document matrices, and officer signature blocks.

---

## 2. Database Schema

The database uses 11 normalized relational entities:

- `users`: User identity, hashed credentials, assigned role (`institution_admin`, `review_officer`, `system_admin`), and institution linkage.
- `institutions`: Institutional registry, AISHE/AICTE permanent code, address, state, district, contact records.
- `applications`: Application lifecycle entity, reference ID (`AICTE-2026-XXXX`), intake count, faculty strength, land acreage, built-up area, compliance score, and risk level (`low`, `medium`, `high`).
- `documents`: Uploaded file manifest, file storage path, MIME type, size, verification status, and provider metadata.
- `document_extractions`: Extracted entity key-value pairs, normalized text, OCR method, and confidence metric.
- `verification_findings`: Explainable validation findings, severity flags, source document citation, and verbatim text quotes.
- `compliance_rules`: Active AICTE regulatory rules, required document prerequisites, and validation thresholds.
- `compliance_results`: Application compliance status per rule (`satisfied`, `not_satisfied`, `requires_human_review`, `insufficient_evidence`).
- `review_decisions`: Officer review records, final decisions (`mark_complete_approved`, `reject_application`, `request_clarification`, `request_correction`), deficiency queries, and institution responses.
- `notifications`: User notifications for application updates, clarification requests, and decisions.
- `audit_logs`: Append-only security ledger tracking all user actions, logins, uploads, and decisions.

---

## 3. SIH Evaluation Demonstration Scenarios

| Scenario | Institution Name | Status | Key Feature Tested |
|---|---|---|---|
| **Scenario 1** | Apex Institute of Technology & Engineering | Approved (100% Score) | Fully valid application; 4 verified documents; zero discrepancies; Low risk profile. |
| **Scenario 2** | Bharati Academy of Technical Studies | Correction Requested | Missing mandatory Land Title Deed; rule engine flags statutory non-compliance; High risk profile. |
| **Scenario 3** | Global Institute of Technology | Clarification Requested | Institution Name Mismatch between Application Form and Registration Certificate; Explainable AI highlights verbatim text and recommends human clarification. |

---

## 4. API Endpoints

- `POST /api/auth/login`: Authenticate user and receive JWT.
- `POST /api/auth/register`: Register institution account.
- `GET /api/auth/me`: Get current user profile.
- `GET /api/applications/`: List applications (role-filtered).
- `GET /api/applications/{id}`: Detailed application audit object.
- `POST /api/applications/`: Create new multi-step application.
- `POST /api/applications/{id}/submit`: Finalize submission and trigger AI scrutiny.
- `POST /api/documents/upload/{app_id}`: Multipart document upload and instant OCR extraction.
- `GET /api/documents/{id}/download`: Authenticated document download.
- `GET /api/compliance/rules`: List configured statutory rules.
- `POST /api/compliance/rules`: Add new compliance rule (System Admin).
- `GET /api/reviews/queue`: Officer review queue with filters.
- `POST /api/reviews/{id}/decision`: Record officer review decision.
- `POST /api/reviews/{id}/clarification-response`: Submit institution clarification.
- `GET /api/reports/compliance/{id}`: Stream ReportLab official PDF report.
- `GET /api/analytics/overview`: High-level metrics for dashboard charts.
- `POST /api/demo/reset`: Reset demonstration database to pristine state.
