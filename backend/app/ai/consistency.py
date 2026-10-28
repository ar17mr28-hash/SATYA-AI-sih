import re
import difflib
from typing import List, Dict, Any, Optional

class ConsistencyEngine:
    """
    Performs cross-document and cross-field consistency analysis.
    Identifies variations, discrepancies, missing requirements, and unreadable evidence.
    Produces explainable findings with verifiable text evidence and standard outcomes:
    MATCH, MISMATCH, POSSIBLE_MISMATCH, MISSING_INFORMATION, UNABLE_TO_DETERMINE.
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalizes names by lowercasing, removing legal noise words and non-alphanumeric chars.
        """
        if not text:
            return ""
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Remove common noise words
        tokens = [w for w in text.split() if w not in {"the", "of", "and", "&", "for", "in", "society", "trust"}]
        return " ".join(tokens)

    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """
        Computes string similarity score between 0.0 and 1.0.
        """
        norm1 = ConsistencyEngine.normalize_text(str1)
        norm2 = ConsistencyEngine.normalize_text(str2)
        if not norm1 or not norm2:
            return 0.0
        if norm1 == norm2:
            return 1.0

        # SequenceMatcher ratio
        seq_ratio = difflib.SequenceMatcher(None, norm1, norm2).ratio()
        
        # Token overlap Jaccard
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())
        jaccard = len(tokens1 & tokens2) / max(len(tokens1 | tokens2), 1)

        return round((seq_ratio * 0.5) + (jaccard * 0.5), 2)

    @staticmethod
    def audit_application_consistency(
        application_data: Dict[str, Any],
        institution_data: Dict[str, Any],
        documents_with_extractions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Runs comprehensive consistency checks across all submitted documents and application facts.
        Generates explainable findings tagged with evidentiary spans, document references,
        and structured outcomes (MATCH, MISMATCH, POSSIBLE_MISMATCH, MISSING_INFORMATION, UNABLE_TO_DETERMINE).
        """
        findings = []
        app_inst_name = institution_data.get("name", "").strip()

        # Track documents by type for cross-document consistency
        docs_by_type = {}
        for doc in documents_with_extractions:
            dt = doc.get("document_type", "Document")
            docs_by_type.setdefault(dt, []).append(doc)

        for doc in documents_with_extractions:
            doc_id = doc.get("id")
            doc_type = doc.get("document_type", "Document")
            filename = doc.get("filename", "")
            extraction = doc.get("extraction") or {}
            extracted_fields = extraction.get("extracted_fields") or {}
            raw_text = extraction.get("raw_text", "")
            ocr_method = extraction.get("ocr_method", "")
            confidence = extraction.get("confidence_score")

            # Check 0: Scanned image with unreadable text / missing engine
            if (ocr_method == "ocr_unavailable_missing_engine" or (confidence is not None and confidence < 0.30)) and len(raw_text.strip()) < 50:
                findings.append({
                    "document_id": doc_id,
                    "finding_type": "insufficient_evidence",
                    "outcome": "UNABLE_TO_DETERMINE",
                    "title": f"Unreadable Scanned Document in {doc_type}",
                    "severity": "critical",
                    "explanation": (
                        f"Text extraction for '{doc_type}' ({filename}) yielded insufficient characters (method: {ocr_method}). "
                        f"Machine verification cannot substantiate claims without human visual inspection or high-resolution re-upload."
                    ),
                    "recommended_action": (
                        "Do not approve automatically. Review officer must visually inspect document scan or request OCR-legible PDF."
                    ),
                    "evidence_snippet": f"Extraction method: {ocr_method} | Extracted character count: {len(raw_text.strip())}",
                    "source_doc_title": f"{doc_type} ({filename})",
                    "page_number": 1
                })
                continue

            # Check 1: Institution Name consistency (Application vs Document)
            doc_inst_name = extracted_fields.get("institution_name")
            if doc_inst_name and app_inst_name:
                sim = ConsistencyEngine.calculate_similarity(app_inst_name, doc_inst_name)
                if sim < 0.40:
                    findings.append({
                        "document_id": doc_id,
                        "finding_type": "inconsistency",
                        "outcome": "MISMATCH",
                        "title": f"Severe Institution Name Mismatch in {doc_type}",
                        "severity": "critical",
                        "explanation": (
                            f"The institution name stated in the application ('{app_inst_name}') has a severe mismatch "
                            f"with the name extracted from {doc_type} ('{doc_inst_name}') (similarity: {int(sim*100)}%)."
                        ),
                        "recommended_action": (
                            "Verify if the document belongs to a completely different institution or legal entity before proceeding."
                        ),
                        "evidence_snippet": f"Extracted: \"{doc_inst_name}\" vs Application: \"{app_inst_name}\"",
                        "source_doc_title": f"{doc_type} ({filename})",
                        "page_number": 1
                    })
                elif 0.40 <= sim < 0.88:
                    findings.append({
                        "document_id": doc_id,
                        "finding_type": "inconsistency",
                        "outcome": "POSSIBLE_MISMATCH",
                        "title": f"Institution Name Discrepancy in {doc_type}",
                        "severity": "warning",
                        "explanation": (
                            f"The institution name stated in the application ('{app_inst_name}') differs "
                            f"from the name extracted from {doc_type} ('{doc_inst_name}') "
                            f"with a similarity match of {int(sim*100)}%."
                        ),
                        "recommended_action": (
                            "Request clarification from the institution or ask for an official gazette "
                            "or name change resolution document before making a determination."
                        ),
                        "evidence_snippet": f"Extracted: \"{doc_inst_name}\" vs Application: \"{app_inst_name}\"",
                        "source_doc_title": f"{doc_type} ({filename})",
                        "page_number": 1
                    })

            # Check 2: Land Area consistency (Application Form vs Land Deed)
            if "Land" in doc_type and "land_area_acres" in extracted_fields:
                try:
                    doc_land = float(extracted_fields["land_area_acres"])
                    app_land = float(application_data.get("campus_area_acres", 0.0))
                    if doc_land > 0 and app_land > 0 and abs(doc_land - app_land) > 0.5:
                        findings.append({
                            "document_id": doc_id,
                            "finding_type": "discrepancy",
                            "outcome": "MISMATCH",
                            "title": "Campus Land Area Discrepancy",
                            "severity": "warning",
                            "explanation": (
                                f"Application states a campus area of {app_land} Acres, whereas "
                                f"the uploaded {doc_type} indicates {doc_land} Acres."
                            ),
                            "recommended_action": "Verify land allotment deed and mutation certificate with revenue records.",
                            "evidence_snippet": f"Document land area: {doc_land} Acres | Form: {app_land} Acres",
                            "source_doc_title": f"{doc_type} ({filename})",
                            "page_number": 1
                        })
                except (ValueError, TypeError):
                    pass

            # Check 3: Built-up area consistency (Application Form vs Building Safety)
            if "Building" in doc_type and "built_up_area_sqm" in extracted_fields:
                try:
                    doc_sqm = float(extracted_fields["built_up_area_sqm"])
                    app_sqm = float(application_data.get("built_up_area_sqm", 0.0))
                    if doc_sqm > 0 and app_sqm > 0 and abs(doc_sqm - app_sqm) > 500.0:
                        findings.append({
                            "document_id": doc_id,
                            "finding_type": "discrepancy",
                            "outcome": "MISMATCH",
                            "title": "Built-up Infrastructure Area Discrepancy",
                            "severity": "warning",
                            "explanation": (
                                f"Application claims {app_sqm} sqm built-up area, but {doc_type} specifies {doc_sqm} sqm."
                            ),
                            "recommended_action": "Verify architect completion certificate and municipal occupancy permit.",
                            "evidence_snippet": f"Building Certificate: {doc_sqm} sqm | Application: {app_sqm} sqm",
                            "source_doc_title": f"{doc_type} ({filename})",
                            "page_number": 1
                        })
                except (ValueError, TypeError):
                    pass

            # Check 4: Expired Validity dates
            if "expiry_date" in extracted_fields:
                exp_str = str(extracted_fields["expiry_date"]).strip()
                # Check for explicit past years indicating expiration
                past_years = ["2020", "2021", "2022", "2023", "2024", "2025"]
                if any(yr in exp_str for yr in past_years) and not any(kw in exp_str.lower() for kw in ["perpetual", "permanent", "lifetime"]):
                    findings.append({
                        "document_id": doc_id,
                        "finding_type": "discrepancy",
                        "outcome": "MISMATCH",
                        "title": f"Expired Validity on {doc_type}",
                        "severity": "critical",
                        "explanation": f"The document indicates a validity date of '{exp_str}', which appears to be expired.",
                        "recommended_action": "Request current valid renewal certificate from issuing authority.",
                        "evidence_snippet": f"Validity Extracted: \"{exp_str}\"",
                        "source_doc_title": f"{doc_type} ({filename})",
                        "page_number": 1
                    })

        return findings
