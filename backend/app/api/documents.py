import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import User, Application, Document, DocumentExtraction, Notification
from ..schemas.schemas import DocumentOut
from ..services.auth import get_current_user, log_audit
from ..ai.parser import DocumentParser
from ..ai.classifier import DocumentClassifier
from ..ai.extractor import FieldExtractor

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = os.path.join(os.getcwd(), "backend", "uploads")
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

@router.post("/upload/{application_id}", response_model=DocumentOut)
async def upload_document(
    application_id: int,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "institution_admin" and current_user.institution_id != app.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to upload documents for this application")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowable limit of 25MB")

    # Run AI Document Parser
    parsed_result = DocumentParser.extract_text_from_file(file_path, file.content_type)
    raw_text = parsed_result.get("text", "")
    ocr_method = parsed_result.get("ocr_method", "native_pdf")
    parser_conf = parsed_result.get("confidence_score")

    # Run AI Classifier
    classification = DocumentClassifier.classify_document(raw_text, file.filename)

    # Run AI Field Extractor
    extraction_result = FieldExtractor.extract_fields(raw_text, document_type)
    extracted_fields = extraction_result.get("fields", {})
    field_conf = extraction_result.get("overall_confidence")

    # Composite confidence
    final_conf = None
    if parser_conf is not None and field_conf is not None:
        final_conf = round((parser_conf * 0.4) + (field_conf * 0.6), 2)
    elif parser_conf is not None:
        final_conf = parser_conf

    # Save Document
    new_doc = Document(
        application_id=app.id,
        document_type=document_type,
        filename=unique_filename,
        original_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type or "application/pdf",
        verification_status="verified",
        verification_provider="VerifyAI AICTE Scrutiny Engine (Mock Verified)",
        is_simulated=True
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Save Extraction
    new_extraction = DocumentExtraction(
        document_id=new_doc.id,
        extracted_fields=extracted_fields,
        raw_text=raw_text[:8000],  # store primary text block
        ocr_method=ocr_method,
        confidence_score=final_conf,
        extraction_metadata={
            "predicted_category": classification.get("predicted_category"),
            "category_confidence": classification.get("confidence"),
            "matched_keywords": classification.get("matched_keywords"),
            "field_confidences": extraction_result.get("field_confidence"),
            "total_pages": parsed_result.get("total_pages", 1)
        }
    )
    db.add(new_extraction)
    db.commit()
    db.refresh(new_doc)

    log_audit(db, action="DOCUMENT_UPLOADED", resource_type="Document", resource_id=str(new_doc.id), user_id=current_user.id, details={"filename": file.filename, "document_type": document_type})
    return new_doc


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    app = db.query(Application).filter(Application.id == doc.application_id).first()
    if current_user.role == "institution_admin" and current_user.institution_id != app.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File on disk not found")

    return FileResponse(
        path=doc.file_path,
        filename=doc.original_name,
        media_type=doc.mime_type
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    app = db.query(Application).filter(Application.id == doc.application_id).first()
    if current_user.role == "institution_admin" and current_user.institution_id != app.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")

    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    log_audit(db, action="DOCUMENT_DELETED", resource_type="Document", resource_id=str(document_id), user_id=current_user.id)
    return {"message": "Document deleted successfully"}
