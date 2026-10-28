"""
Entity Extraction Module for VerifyAI.
Extracts institutional, legal, land, faculty, and regulatory entities from document text.
Tracks verbatim evidence snippets, extraction methods, and provenance.
Never fabricates missing entities.
"""
import re
from typing import Dict, Any, Optional, Tuple, List

class FieldExtractor:
    """
    Rule-based entity extraction retaining evidentiary provenance for every extracted field.
    """

    @staticmethod
    def extract_fields(text: str, document_type: str = "") -> Dict[str, Any]:
        """
        Extracts structured entities along with exact evidence spans,
        methods, and confidence scores.
        """
        extracted = {}
        provenance = {}

        # 1. Institution Name
        inst_name, inst_span, inst_conf = FieldExtractor._extract_institution_name(text)
        if inst_name:
            extracted["institution_name"] = inst_name
            provenance["institution_name"] = {
                "value": inst_name,
                "evidence_snippet": inst_span,
                "method": "regex_heuristic",
                "confidence": inst_conf
            }

        # 2. Registration / Document Number
        doc_num, doc_span, doc_conf = FieldExtractor._extract_document_number(text)
        if doc_num:
            extracted["document_number"] = doc_num
            provenance["document_number"] = {
                "value": doc_num,
                "evidence_snippet": doc_span,
                "method": "regex_heuristic",
                "confidence": doc_conf
            }

        # 3. Dates (Issue Date & Expiry Date)
        issue_date, issue_span, expiry_date, expiry_span, date_conf = FieldExtractor._extract_dates(text)
        if issue_date:
            extracted["issue_date"] = issue_date
            provenance["issue_date"] = {
                "value": issue_date,
                "evidence_snippet": issue_span,
                "method": "regex_heuristic",
                "confidence": date_conf
            }
        if expiry_date:
            extracted["expiry_date"] = expiry_date
            provenance["expiry_date"] = {
                "value": expiry_date,
                "evidence_snippet": expiry_span,
                "method": "regex_heuristic",
                "confidence": date_conf
            }

        # 4. Issuing Authority
        authority, auth_span, auth_conf = FieldExtractor._extract_issuing_authority(text)
        if authority:
            extracted["issuing_authority"] = authority
            provenance["issuing_authority"] = {
                "value": authority,
                "evidence_snippet": auth_span,
                "method": "regex_heuristic",
                "confidence": auth_conf
            }

        # 5. Land Area (Acres)
        land_area, land_span, land_conf = FieldExtractor._extract_land_area(text)
        if land_area is not None:
            extracted["land_area_acres"] = land_area
            provenance["land_area_acres"] = {
                "value": land_area,
                "evidence_snippet": land_span,
                "method": "regex_heuristic",
                "confidence": land_conf
            }

        # 6. Built-up Area (Sqm)
        built_up, built_span, built_conf = FieldExtractor._extract_built_up_area(text)
        if built_up is not None:
            extracted["built_up_area_sqm"] = built_up
            provenance["built_up_area_sqm"] = {
                "value": built_up,
                "evidence_snippet": built_span,
                "method": "regex_heuristic",
                "confidence": built_conf
            }

        # 7. Faculty Strength
        faculty, fac_span, fac_conf = FieldExtractor._extract_faculty_count(text)
        if faculty is not None:
            extracted["faculty_count"] = faculty
            provenance["faculty_count"] = {
                "value": faculty,
                "evidence_snippet": fac_span,
                "method": "regex_heuristic",
                "confidence": fac_conf
            }

        # Overall average confidence
        if provenance:
            avg_conf = round(sum(p["confidence"] for p in provenance.values()) / len(provenance), 2)
        else:
            avg_conf = None

        return {
            "fields": extracted,
            "provenance": provenance,
            "overall_confidence": avg_conf,
            "field_count": len(extracted)
        }

    @staticmethod
    def _extract_institution_name(text: str) -> Tuple[Optional[str], Optional[str], float]:
        patterns = [
            r"(?:Name of (?:the )?(?:Institution|Institute|College|Academy|University)|Institution Name)\s*[:\-]\s*([A-Za-z0-9\s&.,'()\-]{4,80})",
            r"(?:certify that|granted to)\s+([A-Za-z0-9\s&.,'()\-]{5,80}(?:Institute|College|Academy|University|Polytechnic|Technology|Engineering)[A-Za-z0-9\s&.,'()]*)",
            r"([A-Z][A-Za-z\s&]{3,50}(?:Institute|College|Academy|University)\s+of\s+[A-Za-z\s&]{3,40})"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip().split('\n')[0].strip()
                candidate = re.sub(r'[,.\s]+$', '', candidate)
                if len(candidate) > 4:
                    return candidate, match.group(0).strip(), 0.90
        return None, None, 0.0

    @staticmethod
    def _extract_document_number(text: str) -> Tuple[Optional[str], Optional[str], float]:
        patterns = [
            r"(?:Registration|Certificate|Document|Approval|File|Order)\s*(?:No\.?|Number|Ref|ID)\s*[:\-]?\s*([A-Z0-9/\-]{4,35})",
            r"\b(REG/[A-Z0-9/\-]{4,25})\b",
            r"\b(AICTE/[A-Z0-9/\-]{4,25})\b",
            r"\b([A-Z]{1,4}-\d{4,8})\b"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                return val, match.group(0).strip(), 0.92
        return None, None, 0.0

    @staticmethod
    def _extract_dates(text: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], float]:
        issue_date = None
        issue_span = None
        expiry_date = None
        expiry_span = None

        issue_match = re.search(
            r"(?:Date of Issue|Issued on|Date|Dated)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
            text, re.IGNORECASE
        )
        if issue_match:
            issue_date = issue_match.group(1).strip()
            issue_span = issue_match.group(0).strip()

        expiry_match = re.search(
            r"(?:Valid (?:upto|till|until)|Expiry Date|Expires on|Valid Through)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
            text, re.IGNORECASE
        )
        if expiry_match:
            expiry_date = expiry_match.group(1).strip()
            expiry_span = expiry_match.group(0).strip()

        conf = 0.88 if (issue_date or expiry_date) else 0.0
        return issue_date, issue_span, expiry_date, expiry_span, conf

    @staticmethod
    def _extract_issuing_authority(text: str) -> Tuple[Optional[str], Optional[str], float]:
        patterns = [
            r"(?:Issued by|Issuing Authority|Certified by|Approved by)\s*[:\-]?\s*([A-Za-z0-9\s&.,'()\-]{4,70})",
            r"\b(Sub-Registrar|Registrar of Societies|Charity Commissioner|AICTE|PWD|Municipal Corporation|Director of Technical Education)\b"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                auth = match.group(1).strip().split('\n')[0].strip()
                return auth, match.group(0).strip(), 0.85
        return None, None, 0.0

    @staticmethod
    def _extract_land_area(text: str) -> Tuple[Optional[float], Optional[str], float]:
        patterns = [
            r"(?:Area of Land|Land Area|Total Area|Campus Area|Measuring)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:Acres?|Acre|hectares?)",
            r"(\d+(?:\.\d+)?)\s*(?:Acres?|Acre)\s*(?:of contiguous land|of land|in survey)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    return val, match.group(0).strip(), 0.92
                except ValueError:
                    pass
        return None, None, 0.0

    @staticmethod
    def _extract_built_up_area(text: str) -> Tuple[Optional[float], Optional[str], float]:
        match = re.search(
            r"(?:Built-up Area|Instructional Area|Carpet Area|Total Built-up)\s*[:\-]?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:sqm|sq\.m|square\s+meters?)",
            text, re.IGNORECASE
        )
        if match:
            try:
                val = float(match.group(1).replace(",", ""))
                return val, match.group(0).strip(), 0.90
            except ValueError:
                pass
        return None, None, 0.0

    @staticmethod
    def _extract_faculty_count(text: str) -> Tuple[Optional[int], Optional[str], float]:
        match = re.search(
            r"(?:Total Faculty|Faculty Strength|Teaching Staff|Approved Faculty)\s*[:\-]?\s*(\d+)",
            text, re.IGNORECASE
        )
        if match:
            try:
                val = int(match.group(1))
                return val, match.group(0).strip(), 0.88
            except ValueError:
                pass
        return None, None, 0.0
