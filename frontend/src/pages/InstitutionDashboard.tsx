import React, { useState, useEffect } from 'react';
import {
  FilePlus, ClipboardList, CheckCircle2, Clock, AlertTriangle,
  Download, ArrowRight, RefreshCw, Eye, Sparkles, Building2
} from 'lucide-react';
import { api } from '../services/api';
import { ApplicationItem, User } from '../types';
import { StatusBadge, RiskBadge } from '../components/StatusBadge';

interface InstitutionDashboardProps {
  user: User;
  onNavigate: (path: string) => void;
  onViewApplication: (id: number) => void;
}

export const InstitutionDashboard: React.FC<InstitutionDashboardProps> = ({
  user,
  onNavigate,
  onViewApplication
}) => {
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchApps = async () => {
    try {
      setLoading(true);
      const data = await api.getApplications();
      setApplications(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApps();
  }, []);

  const total = applications.length;
  const underReview = applications.filter(a => a.status === 'under_review' || a.status === 'submitted').length;
  const needsAction = applications.filter(a => a.status === 'clarification_requested' || a.status === 'correction_requested').length;
  const approved = applications.filter(a => a.status === 'approved').length;

  return (
    <div className="space-y-6">
      {/* Header Greeting */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-navy-900 tracking-tight">
              Institutional Application Dashboard
            </h1>
            <span className="bg-emerald-50 text-emerald-700 border border-emerald-300 text-[10px] font-mono font-bold px-2 py-0.5 rounded">
              AFFILIATED
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Logged in as <strong>{user.full_name}</strong> &bull; AICTE Approval Scrutiny Cycle 2026-2027
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchApps}
            className="p-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
            title="Refresh Applications"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-royal-600' : ''}`} />
          </button>
          <button
            onClick={() => onNavigate('/apply')}
            className="flex items-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold text-xs px-4 py-2.5 rounded-xl shadow-md shadow-royal-600/30 transition-all"
          >
            <FilePlus className="w-4 h-4" />
            <span>Create New Application</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Total Applications</span>
            <ClipboardList className="w-4 h-4 text-royal-600" />
          </div>
          <div className="text-2xl font-extrabold text-navy-900 mt-2">{total}</div>
          <p className="text-[11px] text-slate-400 mt-1">Across all academic cycles</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Under Scrutiny</span>
            <Clock className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-extrabold text-blue-600 mt-2">{underReview}</div>
          <p className="text-[11px] text-slate-400 mt-1">AI verified, officer review pending</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Requires Action</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-extrabold text-amber-600 mt-2">{needsAction}</div>
          <p className="text-[11px] text-slate-400 mt-1">Clarification or re-upload requested</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
            <span>Approved / Cleared</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-600 mt-2">{approved}</div>
          <p className="text-[11px] text-slate-400 mt-1">Ready for report download</p>
        </div>
      </div>

      {/* Applications List Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-navy-900">Your Institutional Applications</h3>
            <p className="text-xs text-slate-500">Live verification status and AI compliance scorecard</p>
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs flex flex-col items-center gap-2">
            <RefreshCw className="w-6 h-6 animate-spin text-royal-600" />
            <span>Loading applications from secure registry...</span>
          </div>
        ) : applications.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <Building2 className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-700">No applications found</p>
            <p className="text-xs text-slate-500 mt-1">Submit your first institutional regulatory application to start AI validation.</p>
            <button
              onClick={() => onNavigate('/apply')}
              className="mt-4 inline-flex items-center gap-1.5 bg-royal-600 text-white text-xs font-semibold px-4 py-2 rounded-xl"
            >
              <FilePlus className="w-4 h-4" /> Start Application
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Reference ID</th>
                  <th className="py-3 px-4">Academic Year</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">AI Compliance Score</th>
                  <th className="py-3 px-4">Risk Profile</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-mono font-bold text-royal-700">{app.reference_id}</div>
                      <div className="text-[10px] text-slate-400">
                        {app.institution?.name || 'Technical Institute'}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-700">{app.academic_year}</td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={app.status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-slate-200 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              app.compliance_score >= 80 ? 'bg-emerald-500' : (app.compliance_score >= 50 ? 'bg-amber-500' : 'bg-red-500')
                            }`}
                            style={{ width: `${app.compliance_score}%` }}
                          />
                        </div>
                        <span className="font-mono font-bold text-slate-700">{app.compliance_score}%</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <RiskBadge risk={app.risk_level} />
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <button
                        onClick={() => onViewApplication(app.id)}
                        className="inline-flex items-center gap-1 bg-royal-50 hover:bg-royal-100 text-royal-700 font-medium px-2.5 py-1.5 rounded-lg border border-royal-200 transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </button>

                      <a
                        href={api.getComplianceReportUrl(app.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 bg-slate-50 hover:bg-slate-100 text-slate-700 font-medium px-2.5 py-1.5 rounded-lg border border-slate-200 transition-colors"
                        title="Download Official PDF Compliance Report"
                      >
                        <Download className="w-3.5 h-3.5 text-slate-500" />
                        <span>PDF Report</span>
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
