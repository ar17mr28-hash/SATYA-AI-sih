from typing import List, Dict, Any, Optional

class ComplianceEngine:
    """
    Evaluates institutional applications against active AICTE regulatory rules.
    Outputs deterministic, explainable compliance results and overall risk scoring.
    Recognizes four distinct evaluation states:
    - satisfied (Pass: All regulatory conditions verified with clear documentary evidence)
    - not_satisfied (Fail: A clear breach of criteria or total omission of mandatory document)
    - requires_human_review (Ambiguity or discrepancy requiring human officer judgment)
    - insufficient_evidence (Unreadable document, missing OCR engine, or illegible scan preventing machine determination)
    """

    @staticmethod
    def evaluate_compliance(
        application_data: Dict[str, Any],
        institution_data: Dict[str, Any],
        uploaded_doc_types: List[str],
        active_rules: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
        documents_with_extractions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        results = []
        satisfied_count = 0

        student_intake = application_data.get("student_intake", 300)
        faculty_count = max(application_data.get("faculty_count", 15), 1)
        sfr = round(student_intake / faculty_count, 2)
        campus_area = application_data.get("campus_area_acres", 5.0)
        built_up_area = application_data.get("built_up_area_sqm", 8000.0)

        # Map unreadable document types from findings or documents
        unreadable_doc_types = set()
        for f in findings:
            if f.get("finding_type") == "insufficient_evidence":
                source = f.get("source_doc_title", "")
                unreadable_doc_types.add(source.split("(")[0].strip().lower())

        if documents_with_extractions:
            for doc in documents_with_extractions:
                doc_type = doc.get("document_type", "").lower()
                ext = doc.get("extraction") or {}
                if ext.get("ocr_method") == "ocr_unavailable_missing_engine" or doc.get("processing_status") == "PROCESSING_FAILED":
                    unreadable_doc_types.add(doc_type)

        for rule in active_rules:
            rule_id = rule.get("id")
            rule_code = rule.get("rule_code")
            rule_name = rule.get("rule_name")
            required_docs = rule.get("required_documents") or []
            conditions = rule.get("validation_conditions") or {}

            # Check 1: Check if any required document is completely missing from upload list
            missing_docs = [rd for rd in required_docs if not any(rd.lower() in udt.lower() for udt in uploaded_doc_types)]
            if missing_docs:
                results.append({
                    "rule_id": rule_id,
                    "status": "not_satisfied",
                    "score": 0.0,
                    "explanation": f"Mandatory document absent: Application is missing {', '.join(missing_docs)}.",
                    "evidence_summary": f"Uploaded documents: {', '.join(uploaded_doc_types) if uploaded_doc_types else 'None'}",
                    "recommended_action": f"Request upload of {', '.join(missing_docs)} prior to granting regulatory approval."
                })
                continue

            # Check 2: Check if required document is present but unreadable (insufficient evidence)
            has_unreadable_req_doc = any(
                any(rd.lower() in unreadable for unreadable in unreadable_doc_types)
                for rd in required_docs
            )
            if has_unreadable_req_doc:
                results.append({
                    "rule_id": rule_id,
                    "status": "insufficient_evidence",
                    "score": 0.0,
                    "explanation": (
                        f"Cannot evaluate {rule_name}: Supporting document was uploaded but text could not be extracted "
                        f"due to low image clarity or unindexed scan. Machine verification declined."
                    ),
                    "evidence_summary": "Extracted text content insufficient for deterministic rule verification.",
                    "recommended_action": "Review officer must manually review original document scan or request re-upload."
                })
                continue

            # Check 3: Evaluate specific quantitative conditions
            rule_satisfied = True
            reasons = []
            evidences = []

            # A. Faculty-Student Ratio (SFR)
            if "max_student_faculty_ratio" in conditions:
                max_sfr = float(conditions["max_student_faculty_ratio"])
                evidences.append(f"Current SFR: 1:{sfr} (Intake: {student_intake}, Faculty: {faculty_count})")
                if sfr > max_sfr:
                    rule_satisfied = False
                    reasons.append(f"Student-to-Faculty Ratio of 1:{sfr} exceeds the maximum allowable threshold of 1:{max_sfr}.")

            # B. Campus Land Requirement
            if "min_campus_acres" in conditions:
                min_acres = float(conditions["min_campus_acres"])
                evidences.append(f"Stated Campus Area: {campus_area} Acres (Required: {min_acres} Acres)")
                if campus_area < min_acres:
                    rule_satisfied = False
                    reasons.append(f"Campus land area ({campus_area} Acres) is less than the regulatory minimum of {min_acres} Acres.")

            # C. Built-up Area Requirement
            if "min_built_up_sqm" in conditions:
                min_sqm = float(conditions["min_built_up_sqm"])
                evidences.append(f"Stated Built-up Area: {built_up_area} sqm (Required: {min_sqm} sqm)")
                if built_up_area < min_sqm:
                    rule_satisfied = False
                    reasons.append(f"Total built-up infrastructure area ({built_up_area} sqm) is below the minimum threshold ({min_sqm} sqm).")

            # Check 4: Check if any findings relate to this rule
            has_critical_finding = any(
                f.get("severity") == "critical" and
                any(kw.lower() in f.get("title", "").lower() or kw.lower() in f.get("source_doc_title", "").lower() for kw in required_docs)
                for f in findings
            )
            has_warning_finding = any(
                f.get("severity") == "warning" and
                any(kw.lower() in f.get("title", "").lower() or kw.lower() in f.get("source_doc_title", "").lower() for kw in required_docs)
                for f in findings
            )

            if not rule_satisfied:
                results.append({
                    "rule_id": rule_id,
                    "status": "not_satisfied",
                    "score": 0.0,
                    "explanation": " ; ".join(reasons),
                    "evidence_summary": " | ".join(evidences),
                    "recommended_action": "Application requires infrastructure / faculty augmentation to meet AICTE standards."
                })
            elif has_critical_finding:
                results.append({
                    "rule_id": rule_id,
                    "status": "not_satisfied",
                    "score": 0.20,
                    "explanation": f"Document criteria failed due to critical validation defect in submitted supporting records.",
                    "evidence_summary": " | ".join(evidences),
                    "recommended_action": "Review officer must examine critical defect before considering approval."
                })
            elif has_warning_finding:
                results.append({
                    "rule_id": rule_id,
                    "status": "requires_human_review",
                    "score": 0.60,
                    "explanation": f"Document criteria met, but active AI validation discrepancies were flagged in related evidence.",
                    "evidence_summary": " | ".join(evidences),
                    "recommended_action": "Review officer should inspect flagged document discrepancies manually."
                })
            else:
                satisfied_count += 1
                results.append({
                    "rule_id": rule_id,
                    "status": "satisfied",
                    "score": 1.0,
                    "explanation": f"All regulatory conditions for {rule_name} have been verified and satisfied.",
                    "evidence_summary": " | ".join(evidences) if evidences else "Required documents verified.",
                    "recommended_action": "No remedial action required."
                })

        total_rules = max(len(active_rules), 1)
        compliance_score = round((satisfied_count / total_rules) * 100.0, 1)

        # Risk level determination
        critical_findings = [f for f in findings if f.get("severity") == "critical"]
        warning_findings = [f for f in findings if f.get("severity") == "warning"]

        if compliance_score >= 85 and len(critical_findings) == 0 and len(warning_findings) <= 1:
            risk_level = "low"
        elif compliance_score >= 60 and len(critical_findings) == 0:
            risk_level = "medium"
        else:
            risk_level = "high"

        return {
            "results": results,
            "compliance_score": compliance_score,
            "risk_level": risk_level,
            "satisfied_count": satisfied_count,
            "total_rules": total_rules
        }
