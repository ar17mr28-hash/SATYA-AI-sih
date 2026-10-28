import pytest
from app.verification.claim_extractor import ClaimExtractor
from app.verification.retriever import EvidenceRetriever
from app.verification.verifier import ClaimVerifier
from app.verification.scorer import VerificationScorecard
from app.verification.pipeline import VerificationPipeline

def test_claim_extraction_preserves_spans_and_decimals():
    extractor = ClaimExtractor()
    text = "Apex Institute was founded in 2018. The campus area is 7.5 acres located in Pune."
    claims = extractor.extract_claims(text)

    assert len(claims) == 2
    c1, c2 = claims[0], claims[1]

    # Verify spans trace back exactly to verbatim text
    assert text[c1.start_char : c1.end_char] == c1.text
    assert text[c2.start_char : c2.end_char] == c2.text
    assert "2018" in c1.text
    assert "7.5 acres" in c2.text

def test_numerical_contradiction_detection():
    pipeline = VerificationPipeline()
    response = "The approved intake capacity is 500 students."
    evidence = [
        {
            "source_id": "DOC-1",
            "title": "Approval Letter",
            "text": "Sanctioned annual student intake is 300 students for academic year 2026-2027.",
            "page": 1
        }
    ]
    out = pipeline.verify(response, evidence)
    assert len(out["claims"]) == 1
    assert out["claims"][0]["verdict"] == "CONTRADICTED"
    assert "intake" in out["claims"][0]["discrepancy_details"].lower()
    assert out["scorecard"]["overall_trust_score"] == 0.0

def test_date_contradiction_detection():
    pipeline = VerificationPipeline()
    response = "The foundation was established in 2012."
    evidence = [
        {
            "source_id": "DOC-TRUST",
            "title": "Trust Deed",
            "text": "The trust was established in 2018 under registration number F-991.",
            "page": 1
        }
    ]
    out = pipeline.verify(response, evidence)
    assert out["claims"][0]["verdict"] == "CONTRADICTED"
    assert "2012" in out["claims"][0]["discrepancy_details"]
    assert "2018" in out["claims"][0]["discrepancy_details"]

def test_insufficient_support_detection():
    pipeline = VerificationPipeline()
    response = "The faculty cadre ratio strictly satisfies the 1:15 ratio mandated by regulations."
    evidence = [
        {
            "source_id": "DOC-STAFF",
            "title": "Staff Register",
            "text": "The department employs 25 approved faculty members and lecturers, but cadre designations are pending.",
            "page": 1
        }
    ]
    out = pipeline.verify(response, evidence)
    assert out["claims"][0]["verdict"] == "INSUFFICIENT_SUPPORT"

def test_unverifiable_claim_detection():
    pipeline = VerificationPipeline()
    response = "The institute operates a specialized cryogenic supercomputer facility."
    evidence = [
        {
            "source_id": "DOC-LIB",
            "title": "Library Audit",
            "text": "The central library contains 15000 physical volumes and 45 digital subscriptions.",
            "page": 1
        }
    ]
    out = pipeline.verify(response, evidence)
    assert out["claims"][0]["verdict"] == "UNVERIFIABLE"
    assert out["scorecard"]["unverifiable_count"] == 1

def test_scorecard_calculation_bounds():
    # Empty verdicts test
    sc_empty = VerificationScorecard.calculate_scorecard([])
    assert sc_empty["total_claims"] == 0
    assert sc_empty["overall_trust_score"] == 0.0

    pipeline = VerificationPipeline()
    response = "Apex Institute maintains 7.5 acres in Pune."
    evidence = [
        {
            "source_id": "DOC-LAND",
            "title": "Land Deed",
            "text": "Apex Institute maintains a campus area of 7.5 acres in Pune district.",
            "page": 1
        }
    ]
    out = pipeline.verify(response, evidence)
    assert out["scorecard"]["supported_count"] == 1
    assert out["scorecard"]["faithfulness_score"] == 100.0
    assert out["scorecard"]["overall_trust_score"] > 80.0
    assert out["scorecard"]["confidence_interval"][0] <= out["scorecard"]["overall_trust_score"] <= out["scorecard"]["confidence_interval"][1]
