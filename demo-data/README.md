# VerifyAI Synthetic Demonstration Dataset
**SIH 2026 Problem Statement:** SIH26261 (AICTE)

This directory contains documentation and metadata regarding the synthetic demonstration dataset pre-loaded into VerifyAI for Smart India Hackathon evaluation.

> [!NOTE]
> All demonstration records, institutional identities, registration numbers, and regulatory rules in this prototype are clearly labeled synthetic demonstration data for evaluation purposes.

---

## Pre-loaded Test Accounts

| Role | Name | Email | Password | Pre-loaded Context |
|---|---|---|---|---|
| **AICTE Review Officer** | Dr. Sunita Kulkarni | `officer@aicte.gov.in` | `Officer@123` | Scrutiny review queue with all pending, approved, and flagged applications. |
| **Institution Admin (Scenario 1)** | Prof. Anand Verma | `institution@verifyai.gov.in` | `Admin@123` | Apex Institute of Technology & Engineering (Approved, 100% compliance). |
| **Institution Admin (Scenario 2)** | Dr. Ramesh Rao | `bharati@verifyai.gov.in` | `Bharati@123` | Bharati Academy of Technical Studies (Missing Land Title Deed). |
| **Institution Admin (Scenario 3)** | Dr. V. Ramanathan | `global@verifyai.gov.in` | `Global@123` | Global Institute of Technology (Cross-Document Name Mismatch). |
| **System Admin** | Rajesh Sharma | `sysadmin@aicte.gov.in` | `SysAdmin@123` | Compliance Rule Builder, Institution Registry, and Audit Logs. |

---

## 3 Evaluation Scenarios

### Scenario 1: Fully Valid Application
- **Reference ID:** `AICTE-2026-APEX-8821`
- **Institution:** Apex Institute of Technology & Engineering
- **Status:** Approved & Cleared
- **Uploaded Documents:** Society Registration Certificate, Registered Land Conveyance Deed (8.5 Acres), Fire Safety NOC (14,200 sqm).
- **AI Outcome:** All entities match across documents. 100% compliance score. Low risk profile.

### Scenario 2: Missing Mandatory Document
- **Reference ID:** `AICTE-2026-BHARATI-4419`
- **Institution:** Bharati Academy of Technical Studies
- **Status:** Correction Requested
- **Uploaded Documents:** Society Registration Certificate only. Land Title Deed was omitted.
- **AI Outcome:** Rule `RULE-LAND-REQ` flagged non-compliant. Compliance score dropped to 40%. Critical finding triggered for missing statutory document.

### Scenario 3: Cross-Document Name Inconsistency
- **Reference ID:** `AICTE-2026-GLOBAL-7730`
- **Institution:** Global Institute of Technology
- **Status:** Clarification Requested
- **Uploaded Documents:** Registration Certificate lists *"Global Technical Institute"*, whereas application form lists *"Global Institute of Technology"*.
- **AI Outcome:** Explainable AI calculates a 64% token match. Rather than falsely branding the institution fraudulent, the system flags a Warning and triggers a human clarification request. Verifiable text evidence is cited with exact page coordinates.
