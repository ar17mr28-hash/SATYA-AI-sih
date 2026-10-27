import React from 'react';
import {
  Shield, CheckCircle2, FileText, Cpu, ArrowRight, Lock, Eye,
  Building, ChevronRight, Award, Sparkles, Layers, FileCheck, AlertTriangle
} from 'lucide-react';

interface LandingPageProps {
  onNavigate: (path: string) => void;
  onQuickLogin: (role: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate, onQuickLogin }) => {
  return (
    <div className="min-h-screen bg-slatebg flex flex-col">
      {/* Top AICTE Context Bar */}
      <div className="bg-navy-950 text-slate-400 text-xs py-2 px-4 border-b border-navy-800">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-300">Smart India Hackathon 2026</span>
            <span>&bull;</span>
            <span>Problem Statement ID: <strong className="text-cyan-400">SIH26261</strong></span>
            <span>&bull;</span>
            <span>Organization: <strong className="text-slate-200">AICTE</strong></span>
          </div>
          <div className="flex items-center gap-3 text-[11px]">
            <span className="flex items-center gap-1 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              VerifyAI Engine Online
            </span>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-navy-900 via-navy-800 to-navy-900 text-white pt-20 pb-28 px-4 sm:px-6 lg:px-8 border-b border-navy-700/60">
        {/* Subtle grid background */}
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:24px_24px] pointer-events-none"></div>

        <div className="relative max-w-5xl mx-auto text-center space-y-8">
          <div className="inline-flex items-center gap-2 bg-royal-600/30 border border-royal-400/30 text-cyan-300 px-3.5 py-1.5 rounded-full text-xs font-mono tracking-wide">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            AI-POWERED INSTITUTIONAL SCRUTINY & AUDIT
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Intelligent Verification.<br />
            <span className="bg-gradient-to-r from-cyan-400 via-royal-400 to-blue-300 bg-clip-text text-transparent">
              Trusted Compliance.
            </span>
          </h1>

          <p className="max-w-3xl mx-auto text-base sm:text-xl text-slate-300 font-normal leading-relaxed">
            Transforming institutional application verification through AI-powered document intelligence, automated cross-document validation, and explainable compliance auditing.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <button
              onClick={() => onNavigate('/login')}
              className="flex items-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold px-6 py-3.5 rounded-xl shadow-lg shadow-royal-600/40 hover:shadow-royal-600/60 transition-all text-sm group"
            >
              <span>Get Started</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>

            <button
              onClick={() => onQuickLogin('review_officer')}
              className="flex items-center gap-2 bg-navy-700/80 hover:bg-navy-700 text-slate-200 border border-navy-500 font-semibold px-6 py-3.5 rounded-xl transition-all text-sm"
            >
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Explore Officer Scrutiny Console</span>
            </button>
          </div>

          {/* Demonstration Accounts Quick Launch Bar for Judges */}
          <div className="pt-8">
            <div className="bg-navy-950/80 border border-navy-700/80 rounded-2xl p-5 shadow-2xl max-w-4xl mx-auto backdrop-blur-md">
              <div className="flex items-center justify-between border-b border-navy-800 pb-3 mb-4">
                <span className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <Award className="w-4 h-4 text-cyan-400" />
                  SIH 2026 Judge Demonstration Access (1-Click Login)
                </span>
                <span className="text-[11px] text-slate-400">Pre-loaded Synthetic Scenarios</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
                <button
                  onClick={() => onQuickLogin('review_officer')}
                  className="p-3 rounded-xl bg-navy-900 hover:bg-royal-950/60 border border-navy-700 hover:border-royal-500 transition-all group"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-royal-400">
                    <span>AICTE Review Officer</span>
                    <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                  <div className="text-[11px] text-slate-300 mt-1 font-medium">Dr. Sunita Kulkarni</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Scrutiny queue, AI findings, decision recorder</div>
                </button>

                <button
                  onClick={() => onQuickLogin('institution_admin')}
                  className="p-3 rounded-xl bg-navy-900 hover:bg-emerald-950/60 border border-navy-700 hover:border-emerald-500 transition-all group"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-emerald-400">
                    <span>Institution Admin</span>
                    <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                  <div className="text-[11px] text-slate-300 mt-1 font-medium">Apex Institute (Scenario 1)</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Multi-step submit, documents & reports</div>
                </button>

                <button
                  onClick={() => onQuickLogin('system_admin')}
                  className="p-3 rounded-xl bg-navy-900 hover:bg-purple-950/60 border border-navy-700 hover:border-purple-500 transition-all group"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-purple-400">
                    <span>System Admin</span>
                    <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                  <div className="text-[11px] text-slate-300 mt-1 font-medium">Rajesh Sharma</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Rule builder, registry & system analytics</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Pillars */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="text-xs font-mono font-semibold uppercase tracking-wider text-royal-600 bg-royal-50 px-3 py-1 rounded-full border border-royal-200">
            ENGINE ARCHITECTURE
          </span>
          <h2 className="text-3xl font-bold text-navy-900 mt-3 tracking-tight">
            How VerifyAI Solves Institutional Scrutiny
          </h2>
          <p className="text-slate-600 mt-3 text-sm leading-relaxed">
            Eliminating manual document inconsistencies and statutory non-compliance with transparent AI verification.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-royal-600 flex items-center justify-center mb-4">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-navy-900">Multi-Format OCR Engine</h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              Native PDF extraction and OCR for scanned documents. Categorizes certificates, extracts registration numbers, dates, and authorities.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-cyan-50 text-cyan-600 flex items-center justify-center mb-4">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-navy-900">Cross-Document Matrix</h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              Compares entities across forms and certificates. Detects institution name variations, address mismatches, and expired documents.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-navy-900">Configurable Rules Engine</h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              Evaluates applications against AICTE rules: Student-to-Faculty Ratio (1:20), minimum land parcels (5 Acres), built-up area, and safety NOCs.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-navy-900">Explainable AI (XAI)</h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              No black-box decisions. Every flagged discrepancy cites the source document, page number, verbatim extracted quote, and recommended human action.
            </p>
          </div>
        </div>
      </section>

      {/* Workflow Diagram */}
      <section className="bg-white py-16 border-y border-slate-200 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-navy-900">Automated Regulatory Scrutiny Workflow</h2>
            <p className="text-xs text-slate-500 mt-1">Ensuring authorized human control at every regulatory milestone</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 relative">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <div className="w-8 h-8 rounded-full bg-royal-600 text-white font-mono text-xs font-bold flex items-center justify-center mx-auto mb-2">1</div>
              <h4 className="font-bold text-xs text-navy-900">Application Submit</h4>
              <p className="text-[11px] text-slate-500 mt-1">Multi-step wizard with document uploads</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <div className="w-8 h-8 rounded-full bg-royal-600 text-white font-mono text-xs font-bold flex items-center justify-center mx-auto mb-2">2</div>
              <h4 className="font-bold text-xs text-navy-900">OCR & Extraction</h4>
              <p className="text-[11px] text-slate-500 mt-1">PyMuPDF text parsing & entity normalization</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <div className="w-8 h-8 rounded-full bg-royal-600 text-white font-mono text-xs font-bold flex items-center justify-center mx-auto mb-2">3</div>
              <h4 className="font-bold text-xs text-navy-900">Consistency Audit</h4>
              <p className="text-[11px] text-slate-500 mt-1">Cross-check names, land deeds & expiry</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <div className="w-8 h-8 rounded-full bg-royal-600 text-white font-mono text-xs font-bold flex items-center justify-center mx-auto mb-2">4</div>
              <h4 className="font-bold text-xs text-navy-900">AICTE Rule Check</h4>
              <p className="text-[11px] text-slate-500 mt-1">Deterministic compliance evaluation</p>
            </div>

            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 text-center">
              <div className="w-8 h-8 rounded-full bg-emerald-600 text-white font-mono text-xs font-bold flex items-center justify-center mx-auto mb-2">5</div>
              <h4 className="font-bold text-xs text-emerald-900">Officer Decision</h4>
              <p className="text-[11px] text-emerald-700 mt-1">Approve, reject, or request clarification</p>
            </div>
          </div>
        </div>
      </section>

      {/* Security & Government-Grade Highlights */}
      <section className="py-16 px-4 max-w-7xl mx-auto">
        <div className="bg-gradient-to-br from-navy-900 to-navy-800 text-white rounded-3xl p-8 sm:p-12 shadow-xl border border-navy-700">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div>
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-cyan-400 bg-cyan-950/60 border border-cyan-800 px-3 py-1 rounded-full">
                SECURITY & DATA INTEGRITY
              </span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-4">
                Enterprise Architecture Built for Public Sector Trust
              </h2>
              <p className="text-slate-300 text-xs sm:text-sm mt-3 leading-relaxed">
                VerifyAI adheres to strict data governance standards: private isolated storage, immutable audit ledgers, role-based access control, and zero unauthenticated document exposure.
              </p>
              <div className="grid grid-cols-2 gap-4 mt-6 text-xs text-slate-200">
                <div className="flex items-center gap-2">
                  <Lock className="w-4 h-4 text-emerald-400" />
                  <span>BCrypt & JWT Authentication</span>
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-cyan-400" />
                  <span>Immutable Audit Logs</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileCheck className="w-4 h-4 text-royal-400" />
                  <span>ReportLab Official PDFs</span>
                </div>
                <div className="flex items-center gap-2">
                  <Eye className="w-4 h-4 text-amber-400" />
                  <span>Human-in-the-Loop Signoff</span>
                </div>
              </div>
            </div>

            <div className="bg-navy-950/90 rounded-2xl p-6 border border-navy-700/80 font-mono text-xs">
              <div className="flex items-center justify-between text-slate-400 border-b border-navy-800 pb-2 mb-3">
                <span className="text-[10px] text-cyan-400 font-semibold">VerifyAI Scrutiny Report</span>
                <span className="text-[10px]">PDF Generated</span>
              </div>
              <div className="space-y-2 text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-500">Ref ID:</span>
                  <span className="text-white font-bold">AICTE-2026-APEX-8821</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Institution:</span>
                  <span>Apex Inst. of Tech.</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Compliance Score:</span>
                  <span className="text-emerald-400 font-bold">100.0% (Passed)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Risk Profile:</span>
                  <span className="text-emerald-400 font-bold">LOW RISK</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Digital Seal:</span>
                  <span className="text-cyan-400 text-[10px]">SHA256:e3b0c442...</span>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-navy-800 flex justify-between items-center text-[10px] text-slate-400">
                <span>AICTE Regulatory Verification Cell</span>
                <span className="text-emerald-400 font-semibold">VERIFIED</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto bg-navy-950 text-slate-400 py-8 px-4 border-t border-navy-800 text-xs text-center">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-bold text-slate-200">VerifyAI</span> &bull; Smart India Hackathon 2026 Prototype
          </div>
          <div className="text-[11px] text-slate-400">
            Intelligent Document Authentication & Regulatory Compliance Platform | SIH26261
          </div>
        </div>
      </footer>
    </div>
  );
};
