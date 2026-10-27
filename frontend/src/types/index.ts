export type UserRole = 'institution_admin' | 'review_officer' | 'system_admin';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  institution_id?: number | null;
  is_active: boolean;
  created_at: string;
}

export interface Institution {
  id: number;
  name: string;
  code: string;
  institution_type: string;
  state: string;
  district: string;
  address: string;
  contact_email: string;
  contact_phone: string;
}

export interface DocumentExtraction {
  id: number;
  document_id: number;
  extracted_fields: Record<string, any>;
  raw_text?: string;
  ocr_method: string;
  confidence_score?: number | null;
  extraction_metadata?: Record<string, any>;
}

export interface VerificationFinding {
  id: number;
  application_id: number;
  document_id?: number | null;
  finding_type: string;
  title: string;
  severity: 'info' | 'warning' | 'critical';
  explanation: string;
  recommended_action: string;
  evidence_snippet?: string | null;
  source_doc_title?: string | null;
  page_number?: number | null;
  is_resolved: boolean;
}

export interface DocumentItem {
  id: number;
  application_id: number;
  document_type: string;
  filename: string;
  original_name: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  verification_status: string;
  verification_provider: string;
  is_simulated: boolean;
  uploaded_at: string;
  extraction?: DocumentExtraction | null;
  findings?: VerificationFinding[];
}

export interface ComplianceRule {
  id: number;
  rule_code: string;
  rule_name: string;
  description: string;
  applicable_institution_type: string;
  required_documents: string[];
  validation_conditions: Record<string, any>;
  regulatory_source: string;
  effective_date: string;
  rule_version: string;
  is_active: boolean;
}

export interface ComplianceResult {
  id: number;
  application_id: number;
  rule_id: number;
  status: 'satisfied' | 'not_satisfied' | 'insufficient_evidence' | 'requires_human_review';
  score: number;
  explanation: string;
  evidence_summary?: string | null;
  recommended_action?: string | null;
  rule?: ComplianceRule;
}

export interface ReviewDecision {
  id: number;
  application_id: number;
  officer_id?: number | null;
  decision: string;
  remarks: string;
  clarification_query?: string | null;
  clarification_response?: string | null;
  is_clarification_resolved: boolean;
  decided_at: string;
  officer?: { full_name: string; email: string };
}

export interface ApplicationItem {
  id: number;
  reference_id: string;
  institution_id: number;
  academic_year: string;
  status: 'draft' | 'submitted' | 'under_review' | 'clarification_requested' | 'correction_requested' | 'approved' | 'rejected';
  student_intake: number;
  faculty_count: number;
  campus_area_acres: number;
  built_up_area_sqm: number;
  compliance_score: number;
  risk_level: 'low' | 'medium' | 'high';
  ai_validation_summary?: string | null;
  submitted_at?: string | null;
  created_at: string;
  updated_at: string;
  institution?: Institution;
  courses_offered?: { name: string; intake: number }[];
  documents?: DocumentItem[];
  findings?: VerificationFinding[];
  compliance_results?: ComplianceResult[];
  decisions?: ReviewDecision[];
}

export interface NotificationItem {
  id: number;
  title: string;
  message: string;
  category: 'info' | 'warning' | 'success' | 'action_required';
  is_read: boolean;
  link?: string | null;
  created_at: string;
}

export interface AnalyticsData {
  total_applications: number;
  submitted_applications: number;
  under_review_applications: number;
  approved_applications: number;
  clarification_requested_applications: number;
  correction_requested_applications: number;
  rejected_applications: number;
  average_processing_time_hours: number;
  total_documents_processed: number;
  documents_verified: number;
  status_distribution: { name: string; count: number }[];
  risk_distribution: { name: string; count: number }[];
  common_findings: { title: string; count: number }[];
  compliance_breakdown: { status: string; count: number }[];
}

export interface DemoScenario {
  id: string;
  title: string;
  institution: string;
  reference_id: string;
  description: string;
  expected_result: string;
}
