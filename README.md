# VerifyAI
### Intelligent Document Authentication & Regulatory Compliance Platform
**Smart India Hackathon 2026** &bull; **Problem Statement ID:** SIH26261  
**Organization:** All India Council for Technical Education (AICTE)

---

## Overview

**VerifyAI** is an intelligent, full-stack, enterprise-grade regulatory verification platform engineered for the All India Council for Technical Education (AICTE). The platform automates institutional application processing, statutory document authentication, cross-document consistency verification, and regulatory compliance evaluation with **Explainable AI (XAI)**.

---

## Key Features

1. **Multi-Format Document OCR & Ingestion:**
   - Native vector PDF text parsing via PyMuPDF.
   - Heuristic classification into statutory document categories (Registration Certificate, Land Title Deed, Building Safety NOC, Faculty Lists).
   - Structured key-value entity extraction with realistic confidence metrics.

2. **Cross-Document Consistency Matrix:**
   - Detects name variations, address mismatches, and expired validity across forms and attachments.
   - Uses multi-token similarity scoring to prevent false fraud accusations.

3. **Configurable AICTE Regulatory Rules Engine:**
   - Evaluates mandatory documents, Student-to-Faculty Ratios (SFR $\le$ 1:20), minimum campus land (5.0 Acres), built-up infrastructure areas, and fire safety compliance.

4. **Explainable AI (XAI) Audit Findings:**
   - Cites exact verbatim text quotes, source document titles, page numbers, and actionable remedial guidance for every discrepancy.

5. **Human-in-the-Loop Scrutiny Workflow:**
   - AICTE Review Officers can approve, reject, request clarification, or request document correction.
   - Interactive clarification messaging module with full audit history.

6. **Official PDF Compliance Report Generation:**
   - Generates multi-page, government-styled PDF reports via ReportLab with digital watermarks, SHA-256 integrity seals, and officer signature blocks.

7. **Judge Demonstration Mode:**
   - Persistent top demo banner allowing 1-click switching between **3 pre-seeded SIH evaluation scenarios**.

---

## Technology Stack

- **Frontend:** React 18, TypeScript, Tailwind CSS, Lucide Icons, Vite.
- **Backend:** Python 3.13, FastAPI, Pydantic V2, SQLAlchemy, Uvicorn.
- **Database:** SQLite (local zero-config) / PostgreSQL (production ready).
- **Document Processing:** PyMuPDF, Pillow, OpenCV-ready fallback.
- **Report Generation:** ReportLab PDF Engine.
- **Security:** BCrypt password hashing, PyJWT tokens, Role-Based Access Control (RBAC).

---

## Pre-Loaded Test Accounts for Judges

| Role | Name | Email | Password | Pre-Loaded Demonstration Context |
|---|---|---|---|---|
| **AICTE Review Officer** | Dr. Sunita Kulkarni | `officer@aicte.gov.in` | `Officer@123` | Scrutiny console with review queue, split-view document inspector, and decision recorder. |
| **Institution Admin** | Prof. Anand Verma | `institution@verifyai.gov.in` | `Admin@123` | **Scenario 1:** Apex Institute of Technology (Approved, 100% compliance). |
| **Institution Admin** | Dr. Ramesh Rao | `bharati@verifyai.gov.in` | `Bharati@123` | **Scenario 2:** Bharati Academy (Missing mandatory Land Title Deed). |
| **Institution Admin** | Dr. V. Ramanathan | `global@verifyai.gov.in` | `Global@123` | **Scenario 3:** Global Institute (Name mismatch with Explainable AI finding). |
| **System Admin** | Rajesh Sharma | `sysadmin@aicte.gov.in` | `SysAdmin@123` | Regulatory Rules Builder, Institution Registry, and Audit Trail. |

---

## Quickstart & Local Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*The database automatically creates and seeds the 3 demonstration scenarios on first run.*
- API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## Running Automated Tests

Run the test suite verifying authentication, demo scenario consistency, Explainable AI findings, and compliance rules:

```bash
cd backend
python -m pytest app/tests -v
```

---

## Docker Deployment

To launch the full-stack VerifyAI platform using Docker Compose:

```bash
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
