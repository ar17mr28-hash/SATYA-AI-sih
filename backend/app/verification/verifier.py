"""
Verification Engine for VerifyAI.
Evaluates atomic claims against retrieved evidence chunks using deterministic
numerical, date, entity, and lexical alignment checks.
Assigns verifiable verdicts: SUPPORTED, CONTRADICTED, INSUFFICIENT_SUPPORT, UNVERIFIABLE.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from .claim_extractor import ExtractedClaim
from .retriever import RetrievedEvidence

class ClaimVerdict:
    def __init__(
        self,
        claim: ExtractedClaim,
        verdict: str,  # SUPPORTED, CONTRADICTED, INSUFFICIENT_SUPPORT, UNVERIFIABLE
        confidence: float,
        evidence: Optional[RetrievedEvidence] = None,
        rationale: str = "",
        discrepancy_details: Optional[str] = None,
        limitations: Optional[str] = None,
    ):
        self.claim = claim
        self.verdict = verdict
        self.confidence = confidence
        self.evidence = evidence
        self.rationale = rationale
        self.discrepancy_details = discrepancy_details
        self.limitations = limitations or "Deterministic lexical/numerical check based on supplied ground-truth."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim.claim_id,
            "claim_text": self.claim.text,
            "start_char": self.claim.start_char,
            "end_char": self.claim.end_char,
            "claim_type": self.claim.claim_type,
            "verdict": self.verdict,
            "confidence": round(self.confidence, 3),
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "rationale": self.rationale,
            "discrepancy_details": self.discrepancy_details,
            "limitations": self.limitations,
        }

class ClaimVerifier:
    """
    Deterministic rule-based & lexical verifier.
    Performs factual grounding against retrieved evidence chunks.
    """

    def __init__(self, min_support_similarity: float = 0.35, min_lexical_overlap: float = 0.15):
        self.min_support_similarity = min_support_similarity
        self.min_lexical_overlap = min_lexical_overlap

    def verify_claim(self, claim: ExtractedClaim, retrieved_evidence: List[RetrievedEvidence]) -> ClaimVerdict:
        """
        Evaluates a single claim against retrieved evidence.
        """
        # Case 1: No evidence found at all -> UNVERIFIABLE
        if not retrieved_evidence:
            return ClaimVerdict(
                claim=claim,
                verdict="UNVERIFIABLE",
                confidence=0.90,
                evidence=None,
                rationale="No relevant context or document evidence was found in the indexed sources.",
                discrepancy_details="Missing evidentiary grounding in provided documentation.",
                limitations="Absence of evidence in provided documents does not prove claim is false in the real world."
            )

        best_evidence = retrieved_evidence[0]

        # Case 2: Check for numerical contradictions
        if claim.contains_numbers:
            num_verdict, num_details = self._check_numerical_consistency(claim.text, best_evidence.chunk.content)
            if num_verdict == "CONTRADICTED":
                return ClaimVerdict(
                    claim=claim,
                    verdict="CONTRADICTED",
                    confidence=0.95,
                    evidence=best_evidence,
                    rationale=f"Numerical discrepancy detected against source: {num_details}",
                    discrepancy_details=num_details,
                )

        # Case 3: Check for date/temporal contradictions
        if claim.contains_dates:
            date_verdict, date_details = self._check_date_consistency(claim.text, best_evidence.chunk.content)
            if date_verdict == "CONTRADICTED":
                return ClaimVerdict(
                    claim=claim,
                    verdict="CONTRADICTED",
                    confidence=0.92,
                    evidence=best_evidence,
                    rationale=f"Date/temporal discrepancy detected against source: {date_details}",
                    discrepancy_details=date_details,
                )

        # Case 4: Check for direct negation or conflicting keywords
        negation_verdict, negation_details = self._check_negation(claim.text, best_evidence.chunk.content)
        if negation_verdict == "CONTRADICTED":
            return ClaimVerdict(
                claim=claim,
                verdict="CONTRADICTED",
                confidence=0.88,
                evidence=best_evidence,
                rationale=f"Direct polarity/negation conflict detected: {negation_details}",
                discrepancy_details=negation_details,
            )

        # Case 5: Evaluate support vs insufficient support based on token overlap & similarity
        claim_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-.]+\b", claim.text.lower()))
        evidence_tokens = set(best_evidence.chunk.tokens)
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for", "of", "and", "or", "by", "with", "it", "this", "that"}
        claim_substantive = claim_tokens - stop_words

        if not claim_substantive:
            overlap_ratio = 1.0
        else:
            overlap_ratio = len(claim_substantive & evidence_tokens) / len(claim_substantive)

        # Check if numbers in claim explicitly match in evidence
        has_matching_numbers = False
        claim_numbers = re.findall(r"\b\d+(?:\.\d+)?\b", claim.text)
        if claim_numbers:
            has_matching_numbers = all(num in best_evidence.chunk.content for num in claim_numbers)

        if overlap_ratio >= 0.60 or (has_matching_numbers and overlap_ratio >= 0.45) or (overlap_ratio >= 0.50 and best_evidence.relevance_score >= self.min_support_similarity):
            return ClaimVerdict(
                claim=claim,
                verdict="SUPPORTED",
                confidence=round(min(0.98, 0.70 + (overlap_ratio * 0.28)), 2),
                evidence=best_evidence,
                rationale=f"Claim is directly supported by evidence in {best_evidence.chunk.source_title} (Page {best_evidence.chunk.page_number}). Matched terms: {', '.join(best_evidence.matched_tokens[:4])}.",
                discrepancy_details=None,
            )
        elif best_evidence.relevance_score >= 0.15 and overlap_ratio >= 0.20:
            return ClaimVerdict(
                claim=claim,
                verdict="INSUFFICIENT_SUPPORT",
                confidence=0.75,
                evidence=best_evidence,
                rationale=f"Source mentions related topics ({', '.join(best_evidence.matched_tokens[:3])}), but does not provide complete factual confirmation for all assertions.",
                discrepancy_details="Partial topical overlap without conclusive evidentiary grounding.",
            )
        else:
            return ClaimVerdict(
                claim=claim,
                verdict="UNVERIFIABLE",
                confidence=0.85,
                evidence=best_evidence,
                rationale=f"Closest evidence in {best_evidence.chunk.source_title} lacks sufficient relevance (score: {best_evidence.relevance_score:.2f}) to substantiate the claim.",
                discrepancy_details="Insufficient context in provided references.",
            )

    def _check_numerical_consistency(self, claim_text: str, evidence_text: str) -> Tuple[str, Optional[str]]:
        """
        Compares numbers tightly associated with specific units/metrics,
        tolerating intermediate adjectives like 'full-time faculty' or 'approved intake'.
        """
        unit_patterns = [
            (r"(\d+(?:\.\d+)?)\s*(?:[a-zA-Z-]+\s+)?(?:acres?|hectares?)", "land area (acres)"),
            (r"(\d+(?:\.\d+)?)\s*(?:[a-zA-Z-]+\s+)?(?:sqm|sq\.ft|square\s+meters?)", "built-up area (sqm)"),
            (r"(\d+)\s*(?:[a-zA-Z-]+\s+)?(?:students?|seats?|intake)", "student intake"),
            (r"(?:intake|capacity|seats?)\s*(?:of|is|:)?\s*(\d+)", "student intake"),
            (r"(\d+)\s*(?:[a-zA-Z-]+\s+)?(?:faculty|teachers?|professors?)", "faculty count"),
            (r"(?:faculty|teachers?)\s*(?:of|is|:)?\s*(\d+)", "faculty count"),
        ]

        for pat, label in unit_patterns:
            claim_match = re.search(pat, claim_text, re.IGNORECASE)
            ev_match = re.search(pat, evidence_text, re.IGNORECASE)
            if claim_match and ev_match:
                claim_val = float(claim_match.group(1))
                ev_val = float(ev_match.group(1))
                if abs(claim_val - ev_val) > 0.001:
                    return "CONTRADICTED", f"Claim specifies {label} = {claim_val}, but source records {label} = {ev_val}."

        return "NEUTRAL", None

    def _check_date_consistency(self, claim_text: str, evidence_text: str) -> Tuple[str, Optional[str]]:
        """
        Compares 4-digit years or formatted dates when both mention temporal milestones.
        """
        years_in_claim = re.findall(r"\b(19\d{2}|20\d{2})\b", claim_text)
        years_in_ev = re.findall(r"\b(19\d{2}|20\d{2})\b", evidence_text)

        # If claim asserts establishment year or expiration year
        keywords = ["established", "founded", "approved in", "valid till", "expires", "academic year"]
        for kw in keywords:
            if kw in claim_text.lower() and kw in evidence_text.lower():
                if years_in_claim and years_in_ev and years_in_claim[0] != years_in_ev[0]:
                    return "CONTRADICTED", f"Claim states {kw} in {years_in_claim[0]}, but source records {years_in_ev[0]}."

        return "NEUTRAL", None

    def _check_negation(self, claim_text: str, evidence_text: str) -> Tuple[str, Optional[str]]:
        """
        Detects conflicting polarity (e.g. 'is accredited' vs 'is not accredited' / 'failed accreditation').
        """
        claim_lower = claim_text.lower()
        ev_lower = evidence_text.lower()

        negation_pairs = [
            ("accredited", "not accredited"),
            ("approved", "not approved"),
            ("valid", "invalid"),
            ("valid", "expired"),
            ("compliant", "non-compliant"),
            ("passed", "failed"),
            ("eligible", "ineligible"),
        ]

        for pos, neg in negation_pairs:
            if (pos in claim_lower and neg in ev_lower) or (neg in claim_lower and pos in ev_lower):
                # Ensure it's not a double-negative or identical match
                if not (neg in claim_lower and neg in ev_lower):
                    return "CONTRADICTED", f"Polarity mismatch: assertion of '{pos}' vs evidence of '{neg}'."

        return "NEUTRAL", None
