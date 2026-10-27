import re
import difflib
from typing import List, Dict, Any, Optional

class ConsistencyEngine:
    """
    Performs cross-document and cross-field consistency analysis.
    Identifies variations, discrepancies, and missing requirements,
    producing explainable findings with verifiable text evidence.
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
        """
        findings = []
        app_inst_name = institution_data.get("name", "").strip()

        # 1. Cross-check Institution Name across documents
        for doc in documents_with_extractions:
            doc_id = doc.get("id")
            doc_type = doc.get("document_type", "Document")
            filename = doc.get("filename", "")
            extraction = doc.get("extraction") or {}
            extracted_fields = extraction.get("extracted_fields") or {}
            doc_inst_name = extracted_fields.get("institution_name")

            if doc_inst_name and app_inst_name:
                sim = ConsistencyEngine.calculate_similarity(app_inst_name, doc_inst_name)
                # If similarity is between 0.40 and 0.88, it's a potential discrepancy/mismatch
                if 0.30 <= sim < 0.90:
                    findings.append({
                        "document_id": doc_id,
                        "finding_type": "inconsistency",
                        "title": f"Institution Name Mismatch in {doc_type}",
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

            # Check for land area mismatch if document is Land Document
            if "Land" in doc_type and "land_area_acres" in extracted_fields:
                doc_land = float(extracted_fields["land_area_acres"])
                app_land = float(application_data.get("campus_area_acres", 0.0))
                if doc_land > 0 and app_land > 0 and abs(doc_land - app_land) > 0.5:
                    findings.append({
                        "document_id": doc_id,
                        "finding_type": "discrepancy",
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

            # Check expired document
            if "expiry_date" in extracted_fields:
                exp_str = str(extracted_fields["expiry_date"])
                if "2024" in exp_str or "2023" in exp_str or "2022" in exp_str:
                    findings.append({
                        "document_id": doc_id,
                        "finding_type": "discrepancy",
                        "title": f"Expired Validity on {doc_type}",
                        "severity": "critical",
                        "explanation": f"The document indicates a validity date of '{exp_str}', which appears to be expired.",
                        "recommended_action": "Request current valid renewal certificate from issuing authority.",
                        "evidence_snippet": f"Validity Extracted: \"{exp_str}\"",
                        "source_doc_title": f"{doc_type} ({filename})",
                        "page_number": 1
                    })

        return findings
