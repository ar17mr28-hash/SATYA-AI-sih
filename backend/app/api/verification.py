"""
Verification & Benchmark API Router for VerifyAI.
Endpoints for verifying AI responses, inspecting claim-level grounding evidence,
running reproducible evaluation benchmarks, and reviewing historical runs.
"""
import os
import json
import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..models.models import User, VerificationRun
from ..schemas.schemas import (
    VerifyRequest,
    VerifyResponse,
    VerificationRunSummaryOut,
)
from ..services.auth import get_optional_current_user
from ..verification.pipeline import VerificationPipeline
from ..benchmark.runner import BenchmarkRunner

router = APIRouter(prefix="", tags=["AI Verification & Benchmark"])
pipeline = VerificationPipeline()

@router.post("/verify", response_model=VerifyResponse)
def verify_response(
    request: VerifyRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Verifies an AI response against supplied evidence documents or text passages.
    Extracts atomic claims, grounds them with citations, scans for adversarial manipulation,
    and returns transparent multi-dimensional trust metrics.
    """
    # Convert evidence models to list of dicts
    evidence_dicts = [e.model_dump() for e in request.evidence_sources]

    # Run verification pipeline
    result = pipeline.verify(
        response_text=request.response_text,
        evidence_sources=evidence_dicts,
        query=request.query,
        scan_security=request.scan_security,
    )

    run_id = f"VRUN-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    now = datetime.datetime.utcnow()

    # Persist in DB
    v_run = VerificationRun(
        run_id=run_id,
        user_id=current_user.id if current_user else None,
        query=request.query,
        response_text=request.response_text,
        overall_trust_score=result["scorecard"]["overall_trust_score"],
        faithfulness_score=result["scorecard"]["faithfulness_score"],
        grounding_coverage=result["scorecard"]["grounding_coverage"],
        contradiction_rate=result["scorecard"]["contradiction_rate"],
        risk_rating=result["scorecard"]["risk_rating"],
        total_claims=result["scorecard"]["total_claims"],
        supported_count=result["scorecard"]["supported_count"],
        contradicted_count=result["scorecard"]["contradicted_count"],
        insufficient_count=result["scorecard"]["insufficient_support_count"],
        unverifiable_count=result["scorecard"]["unverifiable_count"],
        claims_data=result["claims"],
        scorecard_data=result["scorecard"],
        security_data=result["security"],
        execution_time_ms=result["execution_time_ms"],
        created_at=now,
    )
    db.add(v_run)
    db.commit()

    return {
        "run_id": run_id,
        "query": request.query,
        "response_text": request.response_text,
        "claims": result["claims"],
        "scorecard": result["scorecard"],
        "security": result["security"],
        "evidence_chunk_count": result["evidence_chunk_count"],
        "execution_time_ms": result["execution_time_ms"],
        "pipeline_version": result["pipeline_version"],
        "created_at": now,
    }

@router.get("/verify/history", response_model=List[VerificationRunSummaryOut])
def list_verification_history(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    Retrieves history of past AI verification runs.
    """
    runs = db.query(VerificationRun).order_by(VerificationRun.created_at.desc()).limit(limit).all()
    return runs

@router.get("/verify/{run_id}", response_model=VerifyResponse)
def get_verification_run(
    run_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves full details of a past verification run by its run ID.
    """
    v_run = db.query(VerificationRun).filter(VerificationRun.run_id == run_id).first()
    if not v_run:
        raise HTTPException(status_code=404, detail="Verification run not found")

    return {
        "run_id": v_run.run_id,
        "query": v_run.query,
        "response_text": v_run.response_text,
        "claims": v_run.claims_data or [],
        "scorecard": v_run.scorecard_data or {},
        "security": v_run.security_data or {},
        "evidence_chunk_count": len(v_run.claims_data or []),
        "execution_time_ms": v_run.execution_time_ms,
        "pipeline_version": "2.0.0",
        "created_at": v_run.created_at,
    }

@router.post("/benchmark/run")
def trigger_benchmark():
    """
    Executes the 20-case reproducible evaluation benchmark on demand and returns fresh metrics.
    """
    runner = BenchmarkRunner()
    metrics = runner.run()
    return metrics

@router.get("/benchmark/latest")
def get_latest_benchmark_results():
    """
    Returns the latest recorded evaluation benchmark results from disk.
    """
    json_path = os.path.join(os.path.dirname(__file__), "..", "benchmark", "benchmark_results.json")
    if not os.path.exists(json_path):
        # Run if not already present
        runner = BenchmarkRunner()
        return runner.run()

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
