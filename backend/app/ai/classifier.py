import re
from typing import Dict, Any

DOCUMENT_CATEGORIES = {
    "Registration Certificate": [
        "certificate of incorporation", "registrar of societies", "trust deed",
        "registration certificate", "society registration", "charitable trust",
        "memorandum of association", "registered under section", "society act"
    ],
    "Land & Infrastructure Document": [
        "sale deed", "gift deed", "lease deed", "khasra", "khatauni", "patta",
        "survey no", "land area", "acres", "hectares", "sub-registrar", "encumbrance",
        "possession certificate", "land conversion"
    ],
    "Building Safety & Fire NOC": [
        "fire safety", "fire service", "no objection certificate", "noc",
        "building safety", "structural stability", "pwd engineer", "fitness certificate",
        "fire fighting", "occupancy certificate"
    ],
    "Faculty Qualification & Appointment": [
        "faculty list", "curriculum vitae", "appointment letter", "phd degree",
        "m.tech", "assistant professor", "professor", "cadre ratio", "teaching staff",
        "selection committee", "joining report"
    ],
    "AICTE Mandatory Disclosure & Approval": [
        "aicte approval", "extension of approval", "mandatory disclosure",
        "all india council for technical education", "permanent institute id",
        "application id", "intake capacity"
    ],
    "Financial Audit / Balance Sheet": [
        "chartered accountant", "auditor's report", "balance sheet",
        "income and expenditure", "fixed assets", "audit report", "form 10b",
        "corpus fund", "depreciation"
    ]
}

class DocumentClassifier:
    @staticmethod
    def classify_document(raw_text: str, filename: str = "") -> Dict[str, Any]:
        """
        Classifies document based on text tokens and file naming indicators.
        Returns category, confidence, and matching keywords.
        """
        combined_text = (filename + " " + raw_text).lower()
        best_category = "Other Supporting Document"
        max_matches = 0
        matched_keywords = []

        for category, keywords in DOCUMENT_CATEGORIES.items():
            matches = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', combined_text)]
            if len(matches) > max_matches:
                max_matches = len(matches)
                best_category = category
                matched_keywords = matches

        confidence = round(min(0.98, 0.65 + (max_matches * 0.08)), 2) if max_matches > 0 else 0.50

        return {
            "predicted_category": best_category,
            "confidence": confidence if max_matches > 0 else None,
            "matched_keywords": matched_keywords,
            "match_count": max_matches
        }
