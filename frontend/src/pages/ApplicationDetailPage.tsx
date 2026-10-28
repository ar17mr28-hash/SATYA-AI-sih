import React, { useState, useEffect } from 'react';
import {
  FileText, Download, CheckCircle2, AlertTriangle, ShieldAlert,
  ArrowLeft, RefreshCw, Send, MessageSquare, ChevronDown, ChevronUp,
  FileCheck, Building2, Eye, ShieldCheck, Scale
} from 'lucide-react';
import { api } from '../services/api';
import { ApplicationItem, User } from '../types';
import { StatusBadge, RiskBadge, ProcessingStatusBadge, AuthenticityStatusBadge } from '../components/StatusBadge';

interface ApplicationDetailPageProps {
  applicationId: number;
  user: User;
  onBack: () => void;
}

export const ApplicationDetailPage: React.FC<ApplicationDetailPageProps> = ({
  applicationId,
  user,
  onBack
}) => {
  const [app, setApp] = useState<ApplicationItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [clarificationText, setClarificationText] = useState('');
  const [sendingClarification, setSendingClarification] = useState(false);
  const [expandedDocId, setExpandedDocId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'documents' | 'findings' | 'compliance' | 'decisions'>('findings');

  const fetchDetails = async () => {
    try {
      setLoading(true);
      const data = await api.getApplication(applicationId);
      setApp(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [applicationId]);

  const handleClarificationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clarificationText.trim()) return;
    try {
      setSendingClarification(true);
      await api.respondToClarification(applicationId, clarificationText);
      setClarificationText('');
      await fetchDetails();
      alert('Clarification response submitted successfully! Application status updated to Under Review.');
    } catch (e: any) {
      alert('Error: ' + e.message);
    } finally {
      setSendingClarification(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center text-xs text-slate-500 space-y-2">
        <RefreshCw className="w-6 h-6 animate-spin text-royal-600 mx-auto" />
        <p>Loading application details & AI scrutiny findings...</p>
      </div>
    );
  }

  if (!app) {
    return (
      <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs">
        <p className="text-red-600 font-semibold">Application not found</p>
        <button onClick={onBack} className="mt-3 text-royal-600 hover:underline">Go Back</button>
      </div>
    );
  }

  const latestClarification = app.decisions?.filter(d => d.decision === 'request_clarification').slice(-1)[0];

  return (
    <div className="space-y-6">
      {/* Top Bar with Reference ID & Back */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors"
            title="Back to applications"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-lg font-extrabold text-navy-900">{app.reference_id}</span>
              <StatusBadge status={app.status} />
              <RiskBadge risk={app.risk_level} />
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              {app.institution?.name} &bull; Academic Year: <strong>{app.academic_year}</strong>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchDetails}
            className="p-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <a
            href={api.getComplianceReportUrl(app.id)}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold text-xs px-4 py-2.5 rounded-xl shadow-md shadow-royal-600/30 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF Report</span>
          </a>
        </div>
      </div>

      {/* Clarification Alert Box if active */}
      {app.status === 'clarification_requested' && latestClarification && !latestClarification.is_clarification_resolved && (
        <div className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center flex-shrink-0 mt-0.5">
              <MessageSquare className="w-4 h-4" />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-sm text-amber-900">
                Action Required: AICTE Officer Requested Clarification
              </h3>
              <p className="text-xs text-amber-800 mt-1 leading-relaxed bg-white/70 p-3 rounded-xl border border-amber-200/80">
                "{latestClarification.clarification_query || latestClarification.remarks}"
              </p>
            </div>
          </div>

          <form onSubmit={handleClarificationSubmit} className="space-y-3 pt-1">
            <label className="block text-xs font-semibold text-amber-950">
              Submit Institutional Clarification / Rectification Response:
            </label>
            <textarea
              rows={3}
              required
              placeholder="Provide clarification details, government resolution references, or trade name explanations..."
              value={clarificationText}
              onChange={e => setClarificationText(e.target.value)}
              className="w-full p-3 text-xs border border-amber-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-royal-500"
            />
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={sendingClarification}
                className="flex items-center gap-1.5 bg-amber-600 hover:bg-amber-700 text-white font-semibold text-xs px-4 py-2 rounded-xl transition-all disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{sendingClarification ? 'Submitting...' : 'Submit Clarification'}</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Metrics Card */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs">
          <span className="text-slate-400 block text-[10px] uppercase font-mono">Compliance Score</span>
          <div className="text-xl font-extrabold text-navy-900 mt-1">{app.compliance_score}%</div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2">
            <div
              className={`h-full rounded-full ${app.compliance_score >= 80 ? 'bg-emerald-500' : 'bg-amber-500'}`}
              style={{ width: `${app.compliance_score}%` }}
            />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs">
          <span className="text-slate-400 block text-[10px] uppercase font-mono">Student-Faculty Ratio</span>
          <div className="text-xl font-extrabold text-navy-900 mt-1">
            1:{(app.student_intake / Math.max(app.faculty_count, 1)).toFixed(1)}
          </div>
          <span className="text-[10px] text-slate-500 mt-1 block">
            {app.student_intake} Intake / {app.faculty_count} Faculty
          </span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs">
          <span className="text-slate-400 block text-[10px] uppercase font-mono">Campus Land Area</span>
          <div className="text-xl font-extrabold text-navy-900 mt-1">{app.campus_area_acres} Acres</div>
          <span className="text-[10px] text-slate-500 mt-1 block">Contiguous land title</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs">
          <span className="text-slate-400 block text-[10px] uppercase font-mono">Built-Up Area</span>
          <div className="text-xl font-extrabold text-navy-900 mt-1">{app.built_up_area_sqm.toLocaleString()} sqm</div>
          <span className="text-[10px] text-slate-500 mt-1 block">Instructional space</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 flex gap-6 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('findings')}
          className={`pb-3 flex items-center gap-1.5 transition-colors relative ${
            activeTab === 'findings' ? 'text-royal-600 font-bold border-b-2 border-royal-600' : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          <span>Explainable AI Findings ({app.findings?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('compliance')}
          className={`pb-3 flex items-center gap-1.5 transition-colors relative ${
            activeTab === 'compliance' ? 'text-royal-600 font-bold border-b-2 border-royal-600' : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <Scale className="w-4 h-4" />
          <span>Regulatory Compliance ({app.compliance_results?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('documents')}
          className={`pb-3 flex items-center gap-1.5 transition-colors relative ${
            activeTab === 'documents' ? 'text-royal-600 font-bold border-b-2 border-royal-600' : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Attached Documents ({app.documents?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('decisions')}
          className={`pb-3 flex items-center gap-1.5 transition-colors relative ${
            activeTab === 'decisions' ? 'text-royal-600 font-bold border-b-2 border-royal-600' : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>Officer Remarks & Decisions ({app.decisions?.length || 0})</span>
        </button>
      </div>

      {/* Tab 1: Explainable AI Findings */}
      {activeTab === 'findings' && (
        <div className="space-y-4">
          {(!app.findings || app.findings.length === 0) ? (
            <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-xs">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              <p className="font-bold text-navy-900">Zero Inconsistencies Detected</p>
              <p className="text-slate-500 mt-1">
                The VerifyAI cross-document consistency engine verified that institution names, registration numbers, and dates match across all attached statutory documents.
              </p>
            </div>
          ) : (
            app.findings.map((f) => (
              <div
                key={f.id}
                className={`bg-white p-5 rounded-2xl border shadow-sm space-y-3 ${
                  f.severity === 'critical' ? 'border-red-300 bg-red-50/20' : 'border-amber-300 bg-amber-50/20'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${f.severity === 'critical' ? 'bg-red-500' : 'bg-amber-500'}`}></span>
                    <h4 className="font-bold text-sm text-navy-900">{f.title}</h4>
                  </div>
                  <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${
                    f.severity === 'critical' ? 'bg-red-50 text-red-700 border-red-200' : 'bg-amber-50 text-amber-700 border-amber-200'
                  }`}>
                    {f.severity} SEVERITY
                  </span>
                </div>

                {/* Evidence Snippet */}
                {f.evidence_snippet && (
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs font-mono">
                    <span className="text-[10px] text-slate-400 block font-sans font-semibold mb-1">
                      EXTRACTED TEXT EVIDENCE (Source: {f.source_doc_title || 'Application Manifest'})
                    </span>
                    <span className="text-navy-900 font-semibold">{f.evidence_snippet}</span>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="font-semibold text-slate-500 block mb-0.5">Plain-Language AI Explanation</span>
                    <p className="text-slate-700 leading-relaxed">{f.explanation}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-slate-500 block mb-0.5">Recommended Remedial Action</span>
                    <p className="text-slate-700 leading-relaxed">{f.recommended_action}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 2: Regulatory Compliance */}
      {activeTab === 'compliance' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden text-xs">
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">AICTE Rule</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Evaluated Criteria</th>
                <th className="py-3 px-4">AI Audit Explanation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {app.compliance_results?.map((cr) => (
                <tr key={cr.id} className="hover:bg-slate-50/60">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-navy-900">{cr.rule?.rule_name || 'Statutory Rule'}</div>
                    <div className="text-[10px] font-mono text-royal-600">{cr.rule?.rule_code}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
                      cr.status === 'satisfied'
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                        : cr.status === 'not_satisfied'
                        ? 'bg-red-50 text-red-700 border-red-300'
                        : 'bg-amber-50 text-amber-700 border-amber-300'
                    }`}>
                      {cr.status.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600 font-mono text-[11px]">
                    {cr.evidence_summary || 'Criteria verified'}
                  </td>
                  <td className="py-3.5 px-4 text-slate-700">
                    {cr.explanation}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 3: Documents Vault */}
      {activeTab === 'documents' && (
        <div className="space-y-3">
          {app.documents?.map((d) => (
            <div key={d.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden text-xs">
              <div className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileCheck className="w-5 h-5 text-royal-600" />
                  <div>
                    <div className="font-bold text-navy-900">{d.document_type}</div>
                    <div className="text-[11px] text-slate-500">
                      File: {d.original_name} &bull; {(d.file_size / 1024).toFixed(1)} KB &bull; Provider: {d.verification_provider}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <ProcessingStatusBadge status={d.processing_status} />
                  <AuthenticityStatusBadge status={d.authenticity_status} />
                  {d.file_hash_sha256 && (
                    <span className="hidden md:inline-block font-mono text-[9px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200" title={`SHA-256 Hash: ${d.file_hash_sha256}`}>
                      SHA:{d.file_hash_sha256.substring(0, 8)}...
                    </span>
                  )}

                  <button
                    onClick={() => setExpandedDocId(expandedDocId === d.id ? null : d.id)}
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
                    title="Toggle OCR Extraction"
                  >
                    {expandedDocId === d.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>

                  <a
                    href={api.getDocumentDownloadUrl(d.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 rounded-lg bg-royal-50 text-royal-700 hover:bg-royal-100 border border-royal-200"
                    title="Download original file"
                  >
                    <Download className="w-4 h-4" />
                  </a>
                </div>
              </div>

              {expandedDocId === d.id && d.extraction && (
                <div className="bg-slate-50 border-t border-slate-200 p-4 space-y-3">
                  <div className="flex items-center justify-between text-[11px] text-slate-500 border-b border-slate-200 pb-2">
                    <span>OCR Method: <strong className="font-mono text-navy-900">{d.extraction.ocr_method}</strong></span>
                    <span>Confidence: <strong className="font-mono text-emerald-600">{d.extraction.confidence_score ? `${Math.round(d.extraction.confidence_score * 100)}%` : 'Confidence unavailable'}</strong></span>
                  </div>

                  <div>
                    <span className="font-bold text-[10px] uppercase font-mono text-slate-400 block mb-1">Extracted Key Entities:</span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {Object.entries(d.extraction.extracted_fields || {}).map(([key, val]) => (
                        <div key={key} className="bg-white p-2 rounded-lg border border-slate-200">
                          <span className="text-[10px] text-slate-400 uppercase font-mono">{key.replace(/_/g, ' ')}:</span>
                          <div className="font-semibold text-navy-900">{String(val)}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {d.extraction.raw_text && (
                    <div>
                      <span className="font-bold text-[10px] uppercase font-mono text-slate-400 block mb-1">Raw Extracted OCR Text:</span>
                      <pre className="bg-white p-3 rounded-lg border border-slate-200 text-[10px] font-mono text-slate-700 whitespace-pre-wrap max-h-40 overflow-y-auto">
                        {d.extraction.raw_text}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Tab 4: Officer Decisions & Audit */}
      {activeTab === 'decisions' && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-navy-900">Officer Decision History & Clarification Ledger</h3>
          {(!app.decisions || app.decisions.length === 0) ? (
            <p className="text-xs text-slate-400">No officer decisions recorded yet. Application is currently in automated queue.</p>
          ) : (
            <div className="space-y-3">
              {app.decisions.map((dec) => (
                <div key={dec.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-2">
                  <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                    <span className="font-bold text-navy-900 uppercase tracking-wide font-mono">
                      {dec.decision.replace(/_/g, ' ')}
                    </span>
                    <span className="text-slate-400 font-mono text-[10px]">
                      {new Date(dec.decided_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-slate-700"><strong>Officer Remarks:</strong> {dec.remarks}</p>
                  {dec.clarification_query && (
                    <div className="p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-amber-900">
                      <strong>Query:</strong> {dec.clarification_query}
                    </div>
                  )}
                  {dec.clarification_response && (
                    <div className="p-2.5 bg-blue-50 rounded-lg border border-blue-200 text-blue-900">
                      <strong>Institution Response:</strong> {dec.clarification_response}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
