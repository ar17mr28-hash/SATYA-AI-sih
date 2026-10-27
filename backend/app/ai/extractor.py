import re
import datetime
from typing import Dict, Any, Optional

class FieldExtractor:
    """
    Extracts high-value institutional and regulatory entities from document text.
    Handles date normalization, entity parsing, and confidence scoring.
    """

    @staticmethod
    def extract_fields(text: str, document_type: str = "") -> Dict[str, Any]:
        extracted = {}
        confidence_map = {}

        # 1. Institution Name Extraction
        inst_name, inst_conf = FieldExtractor._extract_institution_name(text)
        if inst_name:
            extracted["institution_name"] = inst_name
            confidence_map["institution_name"] = inst_conf

        # 2. Registration / Document Number Extraction
        doc_num, doc_conf = FieldExtractor._extract_document_number(text)
        if doc_num:
            extracted["document_number"] = doc_num
            confidence_map["document_number"] = doc_conf

        # 3. Dates Extraction (Issue Date, Expiry Date)
        issue_date, expiry_date, date_conf = FieldExtractor._extract_dates(text)
        if issue_date:
            extracted["issue_date"] = issue_date
            confidence_map["issue_date"] = date_conf
        if expiry_date:
            extracted["expiry_date"] = expiry_date
            confidence_map["expiry_date"] = date_conf

        # 4. Issuing Authority
        authority, auth_conf = FieldExtractor._extract_issuing_authority(text)
        if authority:
            extracted["issuing_authority"] = authority
            confidence_map["issuing_authority"] = auth_conf

        # 5. Land Area (Acres/Sqm)
        land_area, land_conf = FieldExtractor._extract_land_area(text)
        if land_area is not None:
            extracted["land_area_acres"] = land_area
            confidence_map["land_area_acres"] = land_conf

        # 6. Overall Confidence Calculation
        if confidence_map:
            avg_conf = round(sum(confidence_map.values()) / len(confidence_map), 2)
        else:
            avg_conf = None  # Confidence unavailable

        return {
            "fields": extracted,
            "field_confidence": confidence_map,
            "overall_confidence": avg_conf
        }

    @staticmethod
    def _extract_institution_name(text: str) -> (Optional[str], float):
        # Look for patterns like "Institution Name: ...", "Name of the Institute: ...", "This is to certify that ... Institute of ..."
        patterns = [
            r"(?:Name of (?:the )?(?:Institution|Institute|College|Academy|University)|Institution Name)\s*[:\-]\s*([A-Za-z0-9\s&.,'()\-]{4,80})",
            r"(?:certify that|granted to)\s+([A-Za-z0-9\s&.,'()\-]{5,80}(?:Institute|College|Academy|University|Polytechnic|Technology|Engineering)[A-Za-z0-9\s&.,'()]*)",
            r"([A-Z][A-Za-z\s&]{3,50}(?:Institute|College|Academy|University)\s+of\s+[A-Za-z\s&]{3,40})"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip().split('\n')[0].strip()
                # Clean trailing commas/periods
                candidate = re.sub(r'[,.\s]+$', '', candidate)
                if len(candidate) > 4:
                    return candidate, 0.92
        return None, 0.0

    @staticmethod
    def _extract_document_number(text: str) -> (Optional[str], float):
        patterns = [
            r"(?:Registration|Certificate|Document|Approval|File|Order)\s*(?:No\.?|Number|Ref|ID)\s*[:\-]?\s*([A-Z0-9/\-]{4,35})",
            r"\b(REG/[A-Z0-9/\-]{4,25})\b",
            r"\b(AICTE/[A-Z0-9/\-]{4,25})\b"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                return val, 0.94
        return None, 0.0

    @staticmethod
    def _extract_dates(text: str) -> (Optional[str], Optional[str], float):
        issue_date = None
        expiry_date = None

        issue_match = re.search(r"(?:Date of Issue|Issued on|Date|Dated)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})", text, re.IGNORECASE)
        if issue_match:
            issue_date = issue_match.group(1).strip()

        expiry_match = re.search(r"(?:Valid (?:Upto|Until|Till)|Expiry Date|Validity)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}|Perpetual|Permanent)", text, re.IGNORECASE)
        if expiry_match:
            expiry_date = expiry_match.group(1).strip()

        return issue_date, expiry_date, 0.90 if (issue_date or expiry_date) else 0.0

    @staticmethod
    def _extract_issuing_authority(text: str) -> (Optional[str], float):
        authorities = [
            "All India Council for Technical Education",
            "AICTE",
            "Registrar of Societies",
            "State Board of Technical Education",
            "Directorate of Technical Education",
            "Department of Higher Education",
            "Sub-Registrar Office",
            "Public Works Department",
            "Fire and Emergency Services Department"
        ]
        for auth in authorities:
            if re.search(r'\b' + re.escape(auth) + r'\b', text, re.IGNORECASE):
                return auth, 0.95
        return None, 0.0

    @staticmethod
    def _extract_land_area(text: str) -> (Optional[float], float):
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:Acres?|acres?|Acre|acre)", text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1)), 0.93
            except ValueError:
                pass
        return None, 0.0
