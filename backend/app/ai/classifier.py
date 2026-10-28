"""
Document Classifier Module for VerifyAI.
Performs transparent, rule-based heuristic classification of institutional documents.
Provides candidate alternatives, explicit classification method attribution,
and triggers review_required when classifications are ambiguous.
"""
import re
from typing import Dict, Any, List

DOCUMENT_CATEGORIES = {
    "Registration Certificate": [
        "certificate of incorporation", "registrar of societies", "trust deed",
        "registration certificate", "society registration", "charitable trust",
        "memorandum of association", "registered under section", "society act",
        "public trust", "trustees"
    ],
    "Land & Infrastructure Document": [
        "sale deed", "gift deed", "lease deed", "khasra", "khatauni", "patta",
        "survey no", "land area", "acres", "hectares", "sub-registrar", "encumbrance",
        "possession certificate", "land conversion", "revenue record", "title deed"
    ],
    "Building Safety & Fire NOC": [
        "fire safety", "fire service", "no objection certificate", "noc",
        "building safety", "structural stability", "pwd engineer", "fitness certificate",
        "fire fighting", "occupancy certificate", "architect certificate"
    ],
    "Faculty Qualification & Appointment": [
        "faculty list", "curriculum vitae", "appointment letter", "phd degree",
        "m.tech", "assistant professor", "professor", "cadre ratio", "teaching staff",
        "selection committee", "joining report", "staff register", "payroll"
    ],
    "AICTE Mandatory Disclosure & Approval": [
        "aicte approval", "extension of approval", "mandatory disclosure",
        "all india council for technical education", "permanent institute id",
        "application id", "intake capacity", "sanctioned intake"
    ],
    "Financial Audit / Balance Sheet": [
        "chartered accountant", "auditor's report", "balance sheet",
        "income and expenditure", "fixed assets", "audit report", "form 10b",
        "corpus fund", "depreciation", "financial year"
    ]
}

class DocumentClassifier:
    """
    Transparent rule-based heuristic classifier.
    Never fabricates calibrated model probabilities; clearly identifies heuristic reasoning.
    """

    @staticmethod
    def classify_document(raw_text: str, filename: str = "") -> Dict[str, Any]:
        """
        Classifies document based on text tokens and file naming indicators.
        Returns predicted category, evidence, alternative candidate classifications,
        and an explicit review_required flag for ambiguous documents.
        """
        combined_text = (filename + " " + raw_text).lower()

        scores: List[Dict[str, Any]] = []

        for category, keywords in DOCUMENT_CATEGORIES.items():
            matched = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', combined_text)]
            if matched:
                scores.append({
                    "category": category,
                    "matched_keywords": matched,
                    "match_count": len(matched)
                })

        scores.sort(key=lambda x: x["match_count"], reverse=True)

        if not scores:
            return {
                "predicted_category": "Other Supporting Document",
                "classification_method": "keyword_heuristic",
                "confidence": None,
                "confidence_label": "Unclassified (No category keywords matched)",
                "matched_keywords": [],
                "match_count": 0,
                "alternative_categories": [],
                "review_required": True,
                "reasoning": "Document contains no statutory classification keywords. Requires human review."
            }

        top = scores[0]
        alternatives = scores[1:3]

        # Check for ambiguity: tie with second place or very weak match (1 keyword only)
        is_ambiguous = False
        if len(scores) > 1 and scores[1]["match_count"] == top["match_count"]:
            is_ambiguous = True
        elif top["match_count"] <= 1 and len(raw_text) > 100:
            is_ambiguous = True

        # Heuristic confidence label
        if top["match_count"] >= 4:
            conf_score = 0.90
            conf_label = "High Confidence (Multiple distinct category keywords matched)"
        elif top["match_count"] >= 2:
            conf_score = 0.75
            conf_label = "Moderate Confidence (Partial keyword match)"
        else:
            conf_score = 0.55
            conf_label = "Low Confidence (Single keyword match; review recommended)"

        return {
            "predicted_category": top["category"],
            "classification_method": "keyword_heuristic",
            "confidence": conf_score,
            "confidence_label": conf_label,
            "matched_keywords": top["matched_keywords"],
            "match_count": top["match_count"],
            "alternative_categories": alternatives,
            "review_required": is_ambiguous,
            "reasoning": f"Matched {top['match_count']} keywords ({', '.join(top['matched_keywords'][:3])}) under {top['category']}."
        }
