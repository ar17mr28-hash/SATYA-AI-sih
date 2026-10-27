import React, { useState, useEffect } from 'react';
import {
  ClipboardList, Search, Filter, CheckCircle2, AlertTriangle, FileWarning,
  Eye, Download, RefreshCw, Send, Check, X, ShieldAlert, FileText,
  Clock, Scale, Sparkles, UserCheck
} from 'lucide-react';
import { api } from '../services/api';
import { ApplicationItem, User } from '../types';
import { StatusBadge, RiskBadge } from '../components/StatusBadge';

interface OfficerReviewPageProps {
  user: User;
  onNavigate: (path: string) => void;
  selectedAppId?: number | null;
}

export const OfficerReviewPage: React.FC<OfficerReviewPageProps> = ({
  user,
  onNavigate,
  selectedAppId
}) => {
  const [queue, setQueue] = useState<ApplicationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeApp, setActiveApp] = useState<ApplicationItem | null>(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');

  // Decision inputs
  const [decisionType, setDecisionType] = useState('mark_complete_approved');
  const [remarks, setRemarks] = useState('All statutory documents and regulatory requirements verified.');
  const [clarificationQuery, setClarificationQuery] = useState('');
  const [submittingDecision, setSubmittingDecision] = useState(false);

  // Inspector View Tab
  const [inspectorTab, setInspectorTab] = useState<'findings' | 'rules' | 'docs' | 'decision'>('findings');
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);

  const fetchQueue = async () => {
    try {
      setLoading(true);
      const data = await api.getReviewQueue(statusFilter, riskFilter, search);
      setQueue(data);
      if (selectedAppId) {
        const found = data.find(a => a.id === selectedAppId);
        if (found) setActiveApp(found);
        else if (data.length > 0) setActiveApp(data[0]);
      } else if (data.length > 0 && !activeApp) {
        setActiveApp(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, [statusFilter, riskFilter]);

  const handleSelectApp = async (appItem: ApplicationItem) => {
    try {
      const full = await api.getApplication(appItem.id);
      setActiveApp(full);
      // Preset remarks according to findings
      if (full.findings && full.findings.length > 0) {
        const topFinding = full.findings[0];
        setDecisionType('request_clarification');
        setRemarks(`AI Scrutiny Flag: ${topFinding.title}. Please provide supporting clarification.`);
        setClarificationQuery(topFinding.recommended_action || '');
      } else {
        setDecisionType('mark_complete_approved');
        setRemarks('Full compliance verified. AI cross-document audit confirmed 100% entity consistency.');
        setClarificationQuery('');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleRecordDecision = async () => {
    if (!activeApp) return;
    try {
      setSubmittingDecision(true);
      await api.recordOfficerDecision(
        activeApp.id,
        decisionType,
        remarks,
        decisionType === 'request_clarification' ? clarificationQuery : undefined
      );
      alert(`Decision recorded successfully: ${decisionType.replace(/_/g, ' ').toUpperCase()}`);
      await fetchQueue();
      const updated = await api.getApplication(activeApp.id);
      setActiveApp(updated);
    } catch (e: any) {
      alert('Error recording decision: ' + e.message);
    } finally {
      setSubmittingDecision(false);
    }
  };

  const handleReaudit = async () => {
    if (!activeApp) return;
    try {
      await api.reauditApplication(activeApp.id);
      const updated = await api.getApplication(activeApp.id);
      setActiveApp(updated);
      alert('AI Verification Pipeline re-executed.');
    } catch (e: any) {
      alert('Error: ' + e.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Officer Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-navy-900 tracking-tight">
              AICTE Scrutiny Officer Console
            </h1>
            <span className="bg-blue-50 text-royal-700 border border-blue-200 text-[10px] font-mono font-bold px-2 py-0.5 rounded">
              OFFICIAL REVIEW
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Authorized Scrutiny Officer: <strong>{user.full_name}</strong> &bull; Human-in-the-Loop Regulatory Verification
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchQueue}
            className="flex items-center gap-1.5 p-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-semibold"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-royal-600' : ''}`} />
            <span>Refresh Queue</span>
          </button>
        </div>
      </div>

      {/* Main Split-View Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Review Queue (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-[750px]">
          <div className="p-4 border-b border-slate-100 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-xs text-navy-900 flex items-center gap-1.5">
                <ClipboardList className="w-4 h-4 text-royal-600" />
                Applications Queue ({queue.length})
              </span>
              <span className="text-[10px] font-mono text-slate-400">SIH26261</span>
            </div>

            {/* Filter row */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
                className="px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-navy-900 focus:outline-none"
              >
                <option value="">All Statuses</option>
                <option value="under_review">Under Review</option>
                <option value="clarification_requested">Clarification Req.</option>
                <option value="correction_requested">Correction Req.</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>

              <select
                value={riskFilter}
                onChange={e => setRiskFilter(e.target.value)}
                className="px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-navy-900 focus:outline-none"
              >
                <option value="">All Risk Levels</option>
                <option value="low">Low Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="high">High Risk</option>
              </select>
            </div>
          </div>

          {/* Queue List Scrollable */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {loading ? (
              <div className="p-12 text-center text-xs text-slate-400">Loading queue...</div>
            ) : queue.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No matching applications in queue.</div>
            ) : (
              queue.map(item => (
                <div
                  key={item.id}
                  onClick={() => handleSelectApp(item)}
                  className={`p-4 cursor-pointer transition-colors text-xs ${
                    activeApp?.id === item.id ? 'bg-royal-50/70 border-l-4 border-royal-600' : 'hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono font-bold text-royal-700">{item.reference_id}</span>
                    <RiskBadge risk={item.risk_level} />
                  </div>
                  <div className="font-semibold text-navy-900 mt-1 line-clamp-1">
                    {item.institution?.name}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">
                    {item.institution?.state} &bull; Intake: {item.student_intake} &bull; Score: <strong>{item.compliance_score}%</strong>
                  </div>
                  <div className="mt-2 flex items-center justify-between">
                    <StatusBadge status={item.status} size="sm" />
                    <span className="text-[10px] text-slate-400">
                      {item.findings?.length || 0} findings
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Inspection Workspace (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {activeApp ? (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              {/* App Banner */}
              <div className="p-5 bg-gradient-to-r from-navy-900 via-navy-800 to-navy-900 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-base text-cyan-300">{activeApp.reference_id}</span>
                    <StatusBadge status={activeApp.status} size="sm" />
                    <RiskBadge risk={activeApp.risk_level} />
                  </div>
                  <h3 className="font-bold text-sm text-white mt-1">{activeApp.institution?.name}</h3>
                  <p className="text-[11px] text-slate-300">
                    Code: {activeApp.institution?.code} &bull; {activeApp.institution?.district}, {activeApp.institution?.state}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleReaudit}
                    className="p-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-300 hover:text-white border border-navy-600 text-xs flex items-center gap-1"
                    title="Re-run AI Scrutiny Pipeline"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Re-Audit</span>
                  </button>

                  <a
                    href={api.getComplianceReportUrl(activeApp.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="p-2 rounded-lg bg-royal-600 hover:bg-royal-500 text-white text-xs font-semibold flex items-center gap-1"
                    title="Download Official Report"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>PDF</span>
                  </a>
                </div>
              </div>

              {/* Sub-tabs */}
              <div className="border-b border-slate-200 px-5 pt-3 flex gap-6 text-xs font-semibold bg-slate-50">
                <button
                  onClick={() => setInspectorTab('findings')}
                  className={`pb-2.5 transition-colors relative flex items-center gap-1.5 ${
                    inspectorTab === 'findings' ? 'text-royal-600 border-b-2 border-royal-600 font-bold' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <ShieldAlert className="w-4 h-4" />
                  <span>Explainable AI Findings ({activeApp.findings?.length || 0})</span>
                </button>

                <button
                  onClick={() => setInspectorTab('rules')}
                  className={`pb-2.5 transition-colors relative flex items-center gap-1.5 ${
                    inspectorTab === 'rules' ? 'text-royal-600 border-b-2 border-royal-600 font-bold' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Scale className="w-4 h-4" />
                  <span>Rule Results ({activeApp.compliance_results?.length || 0})</span>
                </button>

                <button
                  onClick={() => setInspectorTab('docs')}
                  className={`pb-2.5 transition-colors relative flex items-center gap-1.5 ${
                    inspectorTab === 'docs' ? 'text-royal-600 border-b-2 border-royal-600 font-bold' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  <span>Documents ({activeApp.documents?.length || 0})</span>
                </button>

                <button
                  onClick={() => setInspectorTab('decision')}
                  className={`pb-2.5 transition-colors relative flex items-center gap-1.5 ${
                    inspectorTab === 'decision' ? 'text-royal-600 border-b-2 border-royal-600 font-bold' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <UserCheck className="w-4 h-4" />
                  <span>Officer Decision</span>
                </button>
              </div>

              {/* Content Panel */}
              <div className="p-5 max-h-[550px] overflow-y-auto">
                {/* 1. Findings */}
                {inspectorTab === 'findings' && (
                  <div className="space-y-4">
                    {(!activeApp.findings || activeApp.findings.length === 0) ? (
                      <div className="p-8 text-center text-xs text-slate-500 bg-emerald-50/50 rounded-xl border border-emerald-200">
                        <CheckCircle2 className="w-7 h-7 text-emerald-600 mx-auto mb-2" />
                        <span className="font-bold text-emerald-950 block">All Document Entities Consistent</span>
                        <p className="text-[11px] text-emerald-800 mt-1">
                          No name mismatches, address discrepancies, or missing mandatory statutory filings detected.
                        </p>
                      </div>
                    ) : (
                      activeApp.findings.map(f => (
                        <div
                          key={f.id}
                          className={`p-4 rounded-xl border text-xs space-y-2.5 ${
                            f.severity === 'critical' ? 'bg-red-50/40 border-red-200' : 'bg-amber-50/40 border-amber-200'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-navy-900 text-xs">{f.title}</span>
                            <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${
                              f.severity === 'critical' ? 'bg-red-100 text-red-800 border-red-300' : 'bg-amber-100 text-amber-800 border-amber-300'
                            }`}>
                              {f.severity}
                            </span>
                          </div>

                          {f.evidence_snippet && (
                            <div className="bg-white p-2.5 rounded-lg border border-slate-200 font-mono text-[11px] text-slate-800">
                              <span className="text-[9px] uppercase font-sans font-bold text-slate-400 block mb-0.5">
                                Verifiable Text Citation ({f.source_doc_title || 'General'}):
                              </span>
                              "{f.evidence_snippet}"
                            </div>
                          )}

                          <div className="space-y-1">
                            <p className="text-slate-700"><strong>AI Explanation:</strong> {f.explanation}</p>
                            <p className="text-slate-700"><strong>Recommended Officer Action:</strong> {f.recommended_action}</p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}

                {/* 2. Rules */}
                {inspectorTab === 'rules' && (
                  <div className="space-y-3">
                    {activeApp.compliance_results?.map(cr => (
                      <div key={cr.id} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-navy-900">{cr.rule?.rule_name}</span>
                          <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${
                            cr.status === 'satisfied' ? 'bg-emerald-50 text-emerald-700 border-emerald-300' : 'bg-red-50 text-red-700 border-red-300'
                          }`}>
                            {cr.status.replace(/_/g, ' ')}
                          </span>
                        </div>
                        <p className="text-slate-600 text-[11px]"><strong>Evidence:</strong> {cr.evidence_summary}</p>
                        <p className="text-slate-700 text-[11px]">{cr.explanation}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* 3. Documents & Extracted Fields */}
                {inspectorTab === 'docs' && (
                  <div className="space-y-3">
                    {activeApp.documents?.map(d => (
                      <div key={d.id} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="font-bold text-navy-900">{d.document_type}</div>
                          <a
                            href={api.getDocumentDownloadUrl(d.id)}
                            target="_blank"
                            rel="noreferrer"
                            className="text-royal-600 hover:underline flex items-center gap-1 font-semibold text-[11px]"
                          >
                            <Download className="w-3 h-3" /> Download File
                          </a>
                        </div>
                        {d.extraction && (
                          <div className="bg-white p-2.5 rounded-lg border border-slate-200 space-y-1 text-[11px]">
                            <div className="flex justify-between text-slate-400 text-[10px] font-mono">
                              <span>OCR Engine: {d.extraction.ocr_method}</span>
                              <span>Confidence: {d.extraction.confidence_score ? `${Math.round(d.extraction.confidence_score*100)}%` : 'Unavailable'}</span>
                            </div>
                            <div className="font-mono text-slate-700">
                              {Object.entries(d.extraction.extracted_fields || {}).map(([k, v]) => (
                                <div key={k}><strong className="text-navy-900">{k}:</strong> {String(v)}</div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* 4. Decision Maker */}
                {inspectorTab === 'decision' && (
                  <div className="space-y-4 text-xs">
                    <div className="bg-blue-50 border border-blue-200 p-3 rounded-xl text-blue-900">
                      <strong>AICTE Administrative Mandate:</strong> All statutory review decisions are recorded in an immutable audit ledger with the reviewing officer's digital identity.
                    </div>

                    <div>
                      <label className="block font-semibold text-navy-900 mb-1">Administrative Decision</label>
                      <select
                        value={decisionType}
                        onChange={e => setDecisionType(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-xl bg-white font-semibold"
                      >
                        <option value="mark_complete_approved">Mark Complete & Approve Application</option>
                        <option value="request_clarification">Request Clarification from Institution</option>
                        <option value="request_correction">Request Document Correction & Resubmission</option>
                        <option value="reject_application">Reject Application (Statutory Non-Compliance)</option>
                      </select>
                    </div>

                    {decisionType === 'request_clarification' && (
                      <div>
                        <label className="block font-semibold text-amber-900 mb-1">Clarification Query / Deficiency Notice</label>
                        <textarea
                          rows={3}
                          value={clarificationQuery}
                          onChange={e => setClarificationQuery(e.target.value)}
                          placeholder="Specify the exact clarification required regarding legal entity names, missing documents, or revenue deeds..."
                          className="w-full p-2.5 border border-amber-300 rounded-xl bg-amber-50/30 focus:outline-none"
                        />
                      </div>
                    )}

                    <div>
                      <label className="block font-semibold text-navy-900 mb-1">Official Scrutiny Remarks</label>
                      <textarea
                        rows={3}
                        value={remarks}
                        onChange={e => setRemarks(e.target.value)}
                        placeholder="Enter official officer audit observations..."
                        className="w-full p-2.5 border border-slate-300 rounded-xl focus:outline-none"
                      />
                    </div>

                    <button
                      onClick={handleRecordDecision}
                      disabled={submittingDecision}
                      className="w-full bg-royal-600 hover:bg-royal-500 text-white font-bold py-2.5 px-4 rounded-xl shadow-md transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      <Check className="w-4 h-4" />
                      <span>{submittingDecision ? 'Recording Decision...' : 'Record Official Decision'}</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
              Select an institutional application from the queue to start inspection.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
