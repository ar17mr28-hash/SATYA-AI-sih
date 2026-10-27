import React, { useState, useEffect } from 'react';
import {
  Sliders, Plus, CheckCircle2, XCircle, AlertTriangle, BarChart3,
  RefreshCw, Scale, Shield, Building, FileCheck, Layers
} from 'lucide-react';
import { api } from '../services/api';
import { ComplianceRule, AnalyticsData, User } from '../types';

interface AdminDashboardProps {
  user: User;
  onNavigate: (path: string) => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ user, onNavigate }) => {
  const [rules, setRules] = useState<ComplianceRule[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // New Rule Form
  const [ruleCode, setRuleCode] = useState('');
  const [ruleName, setRuleName] = useState('');
  const [description, setDescription] = useState('');
  const [instType, setInstType] = useState('All');
  const [reqDocs, setReqDocs] = useState('Registration Certificate, Land Document');
  const [regSource, setRegSource] = useState('AICTE Approval Process Handbook (Synthetic Demo)');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [rData, aData] = await Promise.all([
        api.getComplianceRules(),
        api.getAnalytics()
      ]);
      setRules(rData);
      setAnalytics(aData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const docList = reqDocs.split(',').map(s => s.trim()).filter(Boolean);
      await api.createComplianceRule({
        rule_code: ruleCode.trim(),
        rule_name: ruleName.trim(),
        description: description.trim(),
        applicable_institution_type: instType,
        required_documents: docList,
        regulatory_source: regSource.trim(),
        is_active: true
      });
      setShowAddModal(false);
      setRuleCode('');
      setRuleName('');
      setDescription('');
      await fetchData();
      alert('Compliance rule created successfully!');
    } catch (e: any) {
      alert('Error creating rule: ' + e.message);
    }
  };

  const toggleRuleActive = async (rule: ComplianceRule) => {
    try {
      await api.updateComplianceRule(rule.id, { is_active: !rule.is_active });
      setRules(prev => prev.map(r => r.id === rule.id ? { ...r, is_active: !r.is_active } : r));
    } catch (e: any) {
      alert('Error updating rule: ' + e.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-navy-900 tracking-tight">
              Regulatory Rules & System Administration
            </h1>
            <span className="bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-mono font-bold px-2 py-0.5 rounded">
              ROOT ADMIN
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Configure statutory AICTE validation policies, audit rules, and scrutinize institutional volumes.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold text-xs px-4 py-2.5 rounded-xl shadow-md transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Compliance Rule</span>
          </button>
        </div>
      </div>

      {/* Analytics Summary */}
      {analytics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-slate-500 text-xs font-semibold">Total Processed</span>
            <div className="text-2xl font-extrabold text-navy-900 mt-1">{analytics.total_applications}</div>
            <div className="text-[11px] text-slate-400 mt-1">Institutional filings</div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-slate-500 text-xs font-semibold">Approved Filings</span>
            <div className="text-2xl font-extrabold text-emerald-600 mt-1">{analytics.approved_applications}</div>
            <div className="text-[11px] text-slate-400 mt-1">Statutory norms verified</div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-slate-500 text-xs font-semibold">Discrepancies Flagged</span>
            <div className="text-2xl font-extrabold text-amber-600 mt-1">{analytics.clarification_requested_applications + analytics.correction_requested_applications}</div>
            <div className="text-[11px] text-slate-400 mt-1">Requiring clarification</div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-slate-500 text-xs font-semibold">Avg. AI Processing Time</span>
            <div className="text-2xl font-extrabold text-royal-600 mt-1">{analytics.average_processing_time_hours} hrs</div>
            <div className="text-[11px] text-slate-400 mt-1">Automated scrutiny cycle</div>
          </div>
        </div>
      )}

      {/* Visual Analytics Charts Section */}
      {analytics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Status Breakdown */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <span className="font-bold text-xs text-navy-900 flex items-center gap-1.5">
                <BarChart3 className="w-4 h-4 text-royal-600" />
                Application Pipeline Distribution
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Live Database</span>
            </div>
            <div className="space-y-3">
              {analytics.status_distribution.map((item, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-600 font-medium">{item.name}</span>
                    <span className="font-mono font-bold text-navy-900">{item.count}</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-royal-600 h-full rounded-full transition-all"
                      style={{ width: `${Math.max((item.count / Math.max(analytics.total_applications, 1)) * 100, 8)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Common Findings / Discrepancies */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <span className="font-bold text-xs text-navy-900 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                Most Common Validation Inconsistencies
              </span>
              <span className="text-[10px] text-slate-400 font-mono">Top Discrepancies</span>
            </div>
            <div className="space-y-2.5">
              {analytics.common_findings.map((f, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                  <span className="font-semibold text-slate-800 line-clamp-1">{f.title}</span>
                  <span className="font-mono font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded text-[10px]">
                    {f.count} instances
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Rules Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden text-xs">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-navy-900">Configured AICTE Regulatory Rules</h3>
            <p className="text-xs text-slate-500">Active validation logic evaluated against applicant submissions</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Rule Code & Name</th>
                <th className="py-3 px-4">Program</th>
                <th className="py-3 px-4">Required Documents</th>
                <th className="py-3 px-4">Regulatory Source</th>
                <th className="py-3 px-4">Version</th>
                <th className="py-3 px-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rules.map(rule => (
                <tr key={rule.id} className="hover:bg-slate-50/60">
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-navy-900">{rule.rule_name}</div>
                    <div className="text-[10px] font-mono text-royal-600">{rule.rule_code}</div>
                    <p className="text-[11px] text-slate-500 mt-0.5">{rule.description}</p>
                  </td>
                  <td className="py-3.5 px-4 font-medium text-slate-700">{rule.applicable_institution_type}</td>
                  <td className="py-3.5 px-4">
                    <div className="flex flex-wrap gap-1">
                      {rule.required_documents.map((d, i) => (
                        <span key={i} className="bg-slate-100 text-slate-700 text-[10px] px-1.5 py-0.5 rounded border border-slate-200">
                          {d}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-500 text-[11px]">{rule.regulatory_source}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-600">{rule.rule_version}</td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => toggleRuleActive(rule)}
                      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase border transition-colors ${
                        rule.is_active
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-300 hover:bg-emerald-100'
                          : 'bg-slate-100 text-slate-500 border-slate-300 hover:bg-slate-200'
                      }`}
                    >
                      {rule.is_active ? 'ACTIVE' : 'DISABLED'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Rule Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-navy-950/70 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 text-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-sm text-navy-900">Add New Regulatory Compliance Rule</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-700 font-bold text-sm">&times;</button>
            </div>

            <form onSubmit={handleCreateRule} className="space-y-3">
              <div>
                <label className="block font-semibold text-navy-900 mb-1">Rule Code (e.g. RULE-LAB-EQUIPMENT)</label>
                <input
                  type="text"
                  required
                  placeholder="RULE-AFFILIATION-NOC"
                  value={ruleCode}
                  onChange={e => setRuleCode(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono uppercase"
                />
              </div>

              <div>
                <label className="block font-semibold text-navy-900 mb-1">Rule Name</label>
                <input
                  type="text"
                  required
                  placeholder="University Affiliation NOC Verification"
                  value={ruleName}
                  onChange={e => setRuleName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl"
                />
              </div>

              <div>
                <label className="block font-semibold text-navy-900 mb-1">Description</label>
                <textarea
                  rows={2}
                  required
                  placeholder="Describes statutory requirement and validation conditions..."
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl"
                />
              </div>

              <div>
                <label className="block font-semibold text-navy-900 mb-1">Mandatory Required Documents (comma-separated)</label>
                <input
                  type="text"
                  value={reqDocs}
                  onChange={e => setReqDocs(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl"
                />
              </div>

              <div>
                <label className="block font-semibold text-navy-900 mb-1">Applicable Program Type</label>
                <select
                  value={instType}
                  onChange={e => setInstType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl bg-white"
                >
                  <option value="All">All Institutions</option>
                  <option value="Engineering & Technology">Engineering & Technology</option>
                  <option value="Management">Management</option>
                  <option value="Polytechnic">Polytechnic</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold rounded-xl"
                >
                  Save Compliance Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
