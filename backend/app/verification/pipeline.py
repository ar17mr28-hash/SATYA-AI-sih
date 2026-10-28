"""
Unified Verification Pipeline Orchestrator for VerifyAI.
Coordinates claim extraction, evidence retrieval, adversarial security scanning,
claim verification, and multi-dimensional scoring into a clean callable pipeline.
"""
import time
from typing import List, Dict, Any, Optional
from .claim_extractor import ClaimExtractor
from .retriever import EvidenceRetriever
from .verifier import ClaimVerifier, ClaimVerdict
from .adversarial import AdversarialDetector
from .scorer import VerificationScorecard

class VerificationPipeline:
    """
    End-to-end AI response and document verification pipeline.
    """

    def __init__(self):
        self.extractor = ClaimExtractor()
        self.verifier = ClaimVerifier()
        self.adversarial_detector = AdversarialDetector()

    def verify(
        self,
        response_text: str,
        evidence_sources: List[Dict[str, Any]],  # [{"source_id": "DOC-1", "title": "AICTE Handbook", "text": "...", "page": 1}]
        query: Optional[str] = None,
        scan_security: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes the full verification workflow.
        """
        start_time = time.perf_counter()

        # Step 1: Security & Adversarial Scan
        security_findings = []
        if scan_security:
            input_scan = self.adversarial_detector.scan_text(response_text, source_label="Response Text")
            if not input_scan["is_safe"]:
                security_findings.append(input_scan)

            if query:
                query_scan = self.adversarial_detector.scan_text(query, source_label="User Query")
                if not query_scan["is_safe"]:
                    security_findings.append(query_scan)

            for src in evidence_sources:
                doc_scan = self.adversarial_detector.scan_text(src.get("text", ""), source_label=f"Evidence: {src.get('title', 'Doc')}")
                if not doc_scan["is_safe"]:
                    security_findings.append(doc_scan)

        # Step 2: Index Evidence Sources
        retriever = EvidenceRetriever()
        for src in evidence_sources:
            retriever.add_document(
                source_id=src.get("source_id", "DOC-001"),
                source_title=src.get("title", "Reference Document"),
                text=src.get("text", ""),
                page_number=src.get("page", 1),
                metadata=src.get("metadata", {}),
            )

        # Step 3: Extract Claims
        claims = self.extractor.extract_claims(response_text)

        # Step 4: Verify Claims against Retrieved Evidence
        verdicts: List[ClaimVerdict] = []
        for claim in claims:
            # Retrieve top 3 relevant evidence chunks for this claim
            retrieved = retriever.retrieve(claim.text, top_k=3)
            verdict = self.verifier.verify_claim(claim, retrieved)
            verdicts.append(verdict)

        # Step 5: Calculate Multi-dimensional Scorecard
        scorecard = VerificationScorecard.calculate_scorecard(verdicts)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "query": query,
            "response_text": response_text,
            "claims": [v.to_dict() for v in verdicts],
            "scorecard": scorecard,
            "security": {
                "is_safe": len(security_findings) == 0,
                "threat_count": len(security_findings),
                "findings": security_findings,
            },
            "evidence_chunk_count": len(retriever.chunks),
            "execution_time_ms": elapsed_ms,
            "pipeline_version": "2.0.0",
        }
