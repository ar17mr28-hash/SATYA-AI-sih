"""
Scoring and Evaluation Metrics Module for VerifyAI.
Calculates multi-dimensional verification metrics:
Faithfulness, Grounding Coverage, Contradiction Rate, and Overall Trust Score.
Avoids false precision and provides transparent methodology notes.
"""
from typing import List, Dict, Any
from .verifier import ClaimVerdict

class VerificationScorecard:
    """
    Computes transparent multi-dimensional verification scores.
    """

    @staticmethod
    def calculate_scorecard(verdicts: List[ClaimVerdict]) -> Dict[str, Any]:
        """
        Calculates individual and composite scores across a set of claim verdicts.
        """
        total_claims = len(verdicts)
        if total_claims == 0:
            return {
                "total_claims": 0,
                "supported_count": 0,
                "contradicted_count": 0,
                "insufficient_support_count": 0,
                "unverifiable_count": 0,
                "faithfulness_score": 0.0,
                "grounding_coverage": 0.0,
                "contradiction_rate": 0.0,
                "overall_trust_score": 0.0,
                "risk_rating": "INCONCLUSIVE",
                "confidence_interval": [0.0, 0.0],
                "methodology_note": "No verifiable factual claims detected in the provided response.",
            }

        supported = sum(1 for v in verdicts if v.verdict == "SUPPORTED")
        contradicted = sum(1 for v in verdicts if v.verdict == "CONTRADICTED")
        insufficient = sum(1 for v in verdicts if v.verdict == "INSUFFICIENT_SUPPORT")
        unverifiable = sum(1 for v in verdicts if v.verdict == "UNVERIFIABLE")

        # Grounding coverage: claims with any matched evidence
        grounded_claims = supported + contradicted + insufficient
        grounding_coverage = (grounded_claims / total_claims) * 100.0

        # Faithfulness: supported claims over all claims with evidence
        if grounded_claims > 0:
            faithfulness = (supported / grounded_claims) * 100.0
        else:
            faithfulness = 0.0

        contradiction_rate = (contradicted / total_claims) * 100.0
        unverifiable_rate = (unverifiable / total_claims) * 100.0

        # Composite Trust Score (0.0 to 100.0)
        # Heavy penalty for direct contradictions, partial reward for grounding
        raw_score = (faithfulness * 0.65) + (grounding_coverage * 0.25) - (contradiction_rate * 0.70)
        trust_score = max(0.0, min(100.0, raw_score))

        # Risk rating
        if contradicted > 0 or trust_score < 50.0:
            risk_rating = "HIGH_RISK"
        elif trust_score < 75.0 or unverifiable_rate > 35.0:
            risk_rating = "MODERATE_RISK"
        else:
            risk_rating = "LOW_RISK"

        # Statistical confidence bounds (+- 5.0% or scaled by claim count)
        margin = max(3.0, 15.0 / (total_claims ** 0.5))
        lower_bound = max(0.0, round(trust_score - margin, 1))
        upper_bound = min(100.0, round(trust_score + margin, 1))

        return {
            "total_claims": total_claims,
            "supported_count": supported,
            "contradicted_count": contradicted,
            "insufficient_support_count": insufficient,
            "unverifiable_count": unverifiable,
            "faithfulness_score": round(faithfulness, 1),
            "grounding_coverage": round(grounding_coverage, 1),
            "contradiction_rate": round(contradiction_rate, 1),
            "unverifiable_rate": round(unverifiable_rate, 1),
            "overall_trust_score": round(trust_score, 1),
            "risk_rating": risk_rating,
            "confidence_interval": [lower_bound, upper_bound],
            "methodology_note": (
                "Score calculated deterministically: 65% weight on claim faithfulness, 25% on grounding coverage, "
                "with an active penalty for direct numerical/factual contradictions. "
                "This score is an estimate based strictly on provided documentation."
            ),
        }
