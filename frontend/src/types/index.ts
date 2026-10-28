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
  processing_status?: 'UPLOADED' | 'PROCESSING' | 'PROCESSED' | 'PROCESSING_FAILED' | string;
  authenticity_status?: 'NOT_CHECKED' | 'CHECKS_PASSED' | 'CHECKS_FAILED' | 'REVIEW_REQUIRED' | 'INCONCLUSIVE' | string;
  file_hash_sha256?: string | null;
  authenticity_checks?: Record<string, any> | null;
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

// ---------------- AI Verification & Benchmark Types ----------------
export interface EvidenceSourceInput {
  source_id: string;
  title: string;
  text: string;
  page?: number;
  metadata?: Record<string, any>;
}

export interface RetrievedEvidence {
  chunk_id: string;
  source_id: string;
  source_title: string;
  page_number: number;
  relevance_score: number;
  matched_tokens: string[];
  verbatim_snippet: string;
}

export interface ClaimVerdict {
  claim_id: string;
  claim_text: string;
  start_char: number;
  end_char: number;
  claim_type: string;
  verdict: 'SUPPORTED' | 'CONTRADICTED' | 'INSUFFICIENT_SUPPORT' | 'UNVERIFIABLE' | 'BLOCKED';
  confidence: number;
  evidence?: RetrievedEvidence | null;
  rationale: string;
  discrepancy_details?: string | null;
  limitations?: string | null;
}

export interface Scorecard {
  total_claims: number;
  supported_count: number;
  contradicted_count: number;
  insufficient_support_count: number;
  unverifiable_count: number;
  faithfulness_score: number;
  grounding_coverage: number;
  contradiction_rate: number;
  unverifiable_rate: number;
  overall_trust_score: number;
  risk_rating: 'LOW_RISK' | 'MODERATE_RISK' | 'HIGH_RISK' | 'INCONCLUSIVE';
  confidence_interval: [number, number];
  methodology_note: string;
}

export interface SecurityScan {
  is_safe: boolean;
  threat_count: number;
  findings: Array<{
    threat_type: string;
    severity: string;
    matched_pattern: string;
    source_label?: string;
    recommendation?: string;
  }>;
}

export interface VerifyResponse {
  run_id: string;
  query?: string | null;
  response_text: string;
  claims: ClaimVerdict[];
  scorecard: Scorecard;
  security: SecurityScan;
  evidence_chunk_count: number;
  execution_time_ms: number;
  pipeline_version: string;
  created_at: string;
}

export interface VerificationRunSummary {
  run_id: string;
  query?: string | null;
  response_text: string;
  overall_trust_score: number;
  faithfulness_score: number;
  risk_rating: string;
  total_claims: number;
  supported_count: number;
  contradicted_count: number;
  execution_time_ms: number;
  created_at: string;
}

export interface BenchmarkMetrics {
  timestamp: string;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix: {
    true_positives: number;
    false_positives: number;
    true_negatives: number;
    false_negatives: number;
  };
  latency: {
    avg_ms: number;
    min_ms: number;
    max_ms: number;
    p95_ms: number;
  };
  baseline_comparison: {
    verifyai_accuracy: number;
    naive_baseline_accuracy: number;
    accuracy_delta: number;
  };
  cases: Array<{
    case_id: string;
    category: string;
    expected: string;
    actual: string;
    passed: boolean;
    latency_ms: number;
    trust_score: number;
  }>;
}

