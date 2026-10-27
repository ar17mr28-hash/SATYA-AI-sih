import React from 'react';
import {
  LayoutDashboard, FilePlus2, FileCheck2, ClipboardList, ShieldAlert,
  Sliders, Building2, History, BarChart3, HelpCircle
} from 'lucide-react';
import { User } from '../types';

interface SidebarProps {
  user: User;
  currentPath: string;
  onNavigate: (path: string) => void;
  isOpen: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  user,
  currentPath,
  onNavigate,
  isOpen,
  onCloseMobile
}) => {
  const role = user.role;

  const renderNavLinks = () => {
    if (role === 'institution_admin') {
      return (
        <>
          <div className="px-3 py-2 text-[10px] font-mono uppercase tracking-wider text-slate-400">
            Institution Services
          </div>
          <button
            onClick={() => onNavigate('/dashboard')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              currentPath === '/dashboard'
                ? 'bg-royal-600 text-white shadow-md shadow-royal-600/30'
                : 'text-slate-300 hover:text-white hover:bg-navy-800'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Overview & Status</span>
          </button>

          <button
            onClick={() => onNavigate('/apply')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              currentPath === '/apply'
                ? 'bg-royal-600 text-white shadow-md shadow-royal-600/30'
                : 'text-slate-300 hover:text-white hover:bg-navy-800'
            }`}
          >
            <FilePlus2 className="w-4 h-4" />
            <span>Submit Application</span>
          </button>

          <button
            onClick={() => onNavigate('/applications')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              currentPath === '/applications'
                ? 'bg-royal-600 text-white shadow-md shadow-royal-600/30'
                : 'text-slate-300 hover:text-white hover:bg-navy-800'
            }`}
          >
            <ClipboardList className="w-4 h-4" />
            <span>Submitted Applications</span>
          </button>
        </>
      );
    }

    if (role === 'review_officer') {
      return (
        <>
          <div className="px-3 py-2 text-[10px] font-mono uppercase tracking-wider text-slate-400">
            Scrutiny & Review
          </div>
          <button
            onClick={() => onNavigate('/officer')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              currentPath === '/officer'
                ? 'bg-royal-600 text-white shadow-md shadow-royal-600/30'
                : 'text-slate-300 hover:text-white hover:bg-navy-800'
            }`}
          >
            <ClipboardList className="w-4 h-4" />
            <span>Review Queue</span>
          </button>

          <button
            onClick={() => onNavigate('/analytics')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              currentPath === '/analytics'
                ? 'bg-royal-600 text-white shadow-md shadow-royal-600/30'
                : 'text-slate-300 hover:text-white hover:bg-navy-800'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Scrutiny Analytics</span>
          </button>
        </>
      );
    }

    if (role === 'system_admin') {
      return (
        <>
          <div className="px-3 py-2 text-[10px] font-mono uppercase tracking-wider text-slate-400">
            System Administration
          </div>
          <button
            onClick={() => onNavigate('/admin')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              currentPath === '/admin'
                ? 'bg-royal-600 text-white shadow-md shadow-royal-600/30'
                : 'text-slate-300 hover:text-white hover:bg-navy-800'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Admin Console</span>
          </button>

          <button
            onClick={() => onNavigate('/admin/rules')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              currentPath === '/admin/rules'
                ? 'bg-royal-600 text-white shadow-md shadow-royal-600/30'
                : 'text-slate-300 hover:text-white hover:bg-navy-800'
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span>Regulatory Rules Builder</span>
          </button>

          <button
            onClick={() => onNavigate('/analytics')}
            className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
              currentPath === '/analytics'
                ? 'bg-royal-600 text-white shadow-md shadow-royal-600/30'
                : 'text-slate-300 hover:text-white hover:bg-navy-800'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Executive Analytics</span>
          </button>
        </>
      );
    }

    return null;
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-navy-950/70 z-40 lg:hidden backdrop-blur-sm"
        />
      )}

      {/* Sidebar Panel */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-50 w-64 bg-navy-900 border-r border-navy-800 flex flex-col transition-transform duration-200 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-4 border-b border-navy-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span className="text-[11px] font-mono uppercase text-slate-300">
              AICTE Regulatory Vault
            </span>
          </div>
          <button
            onClick={onCloseMobile}
            className="text-slate-400 hover:text-white lg:hidden text-xs"
          >
            &times;
          </button>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {renderNavLinks()}
        </nav>

        {/* Footer info card */}
        <div className="p-3 m-3 bg-navy-800/80 rounded-xl border border-navy-700/60 text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5 font-semibold text-slate-200 mb-1">
            <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
            <span>Explainable AI Engine</span>
          </div>
          <p className="text-[10px] leading-relaxed text-slate-400">
            Automated scrutiny with verifiable citations & transparent audit trails.
          </p>
        </div>
      </aside>
    </>
  );
};
