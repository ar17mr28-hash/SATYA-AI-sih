import React, { useState } from 'react';
import { Shield, Lock, Mail, ArrowRight, AlertCircle, Award, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { User } from '../types';

interface LoginPageProps {
  onLoginSuccess: (user: User) => void;
  onNavigate: (path: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess, onNavigate }) => {
  const [email, setEmail] = useState('officer@aicte.gov.in');
  const [password, setPassword] = useState('Officer@123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.login(email, password);
      onLoginSuccess(res.user);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillQuickAccount = (eStr: string, pStr: string) => {
    setEmail(eStr);
    setPassword(pStr);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slatebg flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div
          onClick={() => onNavigate('/')}
          className="inline-flex items-center gap-2 cursor-pointer mb-2"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-royal-600 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-royal-600/30">
            <Shield className="w-6 h-6" />
          </div>
          <span className="font-extrabold text-2xl tracking-tight text-navy-900">
            VerifyAI
          </span>
        </div>
        <h2 className="text-xl font-bold text-navy-900 tracking-tight">
          Regulatory Scrutiny Portal Sign In
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          AICTE Document Verification & Compliance Platform (SIH26261)
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-xl px-4">
        <div className="bg-white py-8 px-6 sm:px-10 shadow-xl rounded-2xl border border-slate-200">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-navy-900 mb-1">
                Authorized Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="officer@aicte.gov.in"
                  className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-xl text-xs text-navy-900 focus:outline-none focus:ring-2 focus:ring-royal-500 focus:border-royal-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-navy-900 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-xl text-xs text-navy-900 focus:outline-none focus:ring-2 focus:ring-royal-500 focus:border-royal-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold py-2.5 px-4 rounded-xl text-xs shadow-md shadow-royal-600/30 transition-all disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating Credentials...' : 'Sign In to VerifyAI'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Login Options for Judges */}
          <div className="mt-8 pt-6 border-t border-slate-200">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 mb-3">
              <Award className="w-4 h-4 text-cyan-600" />
              <span>SIH Judge 1-Click Fast Fill:</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
              <button
                type="button"
                onClick={() => fillQuickAccount('officer@aicte.gov.in', 'Officer@123')}
                className="p-2.5 rounded-lg border border-blue-200 bg-blue-50/60 hover:bg-blue-100/80 transition-colors text-left"
              >
                <div className="text-[11px] font-bold text-royal-700">AICTE Review Officer</div>
                <div className="text-[10px] text-slate-500">Dr. Sunita Kulkarni &bull; Officer@123</div>
              </button>

              <button
                type="button"
                onClick={() => fillQuickAccount('institution@verifyai.gov.in', 'Admin@123')}
                className="p-2.5 rounded-lg border border-emerald-200 bg-emerald-50/60 hover:bg-emerald-100/80 transition-colors text-left"
              >
                <div className="text-[11px] font-bold text-emerald-800">Apex Admin (Scenario 1)</div>
                <div className="text-[10px] text-slate-500">Prof. Anand Verma &bull; Admin@123</div>
              </button>

              <button
                type="button"
                onClick={() => fillQuickAccount('bharati@verifyai.gov.in', 'Bharati@123')}
                className="p-2.5 rounded-lg border border-red-200 bg-red-50/60 hover:bg-red-100/80 transition-colors text-left"
              >
                <div className="text-[11px] font-bold text-red-800">Bharati Admin (Scenario 2)</div>
                <div className="text-[10px] text-slate-500">Dr. Ramesh Rao &bull; Bharati@123</div>
              </button>

              <button
                type="button"
                onClick={() => fillQuickAccount('global@verifyai.gov.in', 'Global@123')}
                className="p-2.5 rounded-lg border border-amber-200 bg-amber-50/60 hover:bg-amber-100/80 transition-colors text-left"
              >
                <div className="text-[11px] font-bold text-amber-800">Global Admin (Scenario 3)</div>
                <div className="text-[10px] text-slate-500">Dr. V. Ramanathan &bull; Global@123</div>
              </button>

              <button
                type="button"
                onClick={() => fillQuickAccount('sysadmin@aicte.gov.in', 'SysAdmin@123')}
                className="p-2.5 rounded-lg border border-purple-200 bg-purple-50/60 hover:bg-purple-100/80 transition-colors text-left sm:col-span-2"
              >
                <div className="text-[11px] font-bold text-purple-800">System Admin</div>
                <div className="text-[10px] text-slate-500">Rajesh Sharma &bull; SysAdmin@123 (Rule Builder & Audits)</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
