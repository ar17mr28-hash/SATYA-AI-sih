from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import User, ComplianceRule, ComplianceResult, Application
from ..schemas.schemas import ComplianceRuleCreate, ComplianceRuleUpdate, ComplianceRuleOut, ComplianceResultOut
from ..services.auth import get_current_user, require_roles, log_audit

router = APIRouter(prefix="/compliance", tags=["Compliance Rules & Results"])

@router.get("/rules", response_model=List[ComplianceRuleOut])
def get_compliance_rules(db: Session = Depends(get_db)):
    return db.query(ComplianceRule).order_by(ComplianceRule.rule_code.asc()).all()

@router.post("/rules", response_model=ComplianceRuleOut)
def create_compliance_rule(
    rule_in: ComplianceRuleCreate,
    current_user: User = Depends(require_roles(["system_admin"])),
    db: Session = Depends(get_db)
):
    existing = db.query(ComplianceRule).filter(ComplianceRule.rule_code == rule_in.rule_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="A rule with this code already exists")

    new_rule = ComplianceRule(
        rule_code=rule_in.rule_code,
        rule_name=rule_in.rule_name,
        description=rule_in.description,
        applicable_institution_type=rule_in.applicable_institution_type,
        required_documents=rule_in.required_documents,
        validation_conditions=rule_in.validation_conditions,
        regulatory_source=rule_in.regulatory_source,
        effective_date=rule_in.effective_date,
        rule_version=rule_in.rule_version,
        is_active=rule_in.is_active
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    log_audit(db, action="COMPLIANCE_RULE_CREATED", resource_type="ComplianceRule", resource_id=str(new_rule.id), user_id=current_user.id)
    return new_rule

@router.put("/rules/{rule_id}", response_model=ComplianceRuleOut)
def update_compliance_rule(
    rule_id: int,
    rule_update: ComplianceRuleUpdate,
    current_user: User = Depends(require_roles(["system_admin"])),
    db: Session = Depends(get_db)
):
    rule = db.query(ComplianceRule).filter(ComplianceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")

    update_dict = rule_update.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)
    log_audit(db, action="COMPLIANCE_RULE_UPDATED", resource_type="ComplianceRule", resource_id=str(rule.id), user_id=current_user.id)
    return rule

@router.get("/results/{application_id}", response_model=List[ComplianceResultOut])
def get_compliance_results(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == "institution_admin" and current_user.institution_id != app.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these compliance results")

    return db.query(ComplianceResult).filter(ComplianceResult.application_id == application_id).all()
