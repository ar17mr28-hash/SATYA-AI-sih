import React from 'react';
import { Shield, UserCheck, LogOut, Menu, User as UserIcon, Zap } from 'lucide-react';
import { User } from '../types';
import { NotificationDropdown } from './NotificationDropdown';

interface NavbarProps {
  user: User | null;
  onLogout: () => void;
  onToggleSidebar?: () => void;
  onNavigate?: (path: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ user, onLogout, onToggleSidebar, onNavigate }) => {
  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'system_admin':
        return <span className="bg-purple-100 text-purple-800 border border-purple-300 text-[10px] font-mono font-semibold px-2 py-0.5 rounded">SYSTEM ADMIN</span>;
      case 'review_officer':
        return <span className="bg-blue-100 text-blue-800 border border-blue-300 text-[10px] font-mono font-semibold px-2 py-0.5 rounded">AICTE REVIEW OFFICER</span>;
      case 'institution_admin':
      default:
        return <span className="bg-emerald-100 text-emerald-800 border border-emerald-300 text-[10px] font-mono font-semibold px-2 py-0.5 rounded">INSTITUTION ADMIN</span>;
    }
  };

  return (
    <header className="bg-navy-900 border-b border-navy-800 text-white sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left Brand */}
          <div className="flex items-center gap-3">
            {user && (
              <button
                onClick={onToggleSidebar}
                className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-navy-800 lg:hidden"
                aria-label="Toggle Navigation"
              >
                <Menu className="w-5 h-5" />
              </button>
            )}

            <div
              onClick={() => onNavigate && onNavigate('/')}
              className="flex items-center gap-2.5 cursor-pointer select-none group"
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-royal-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-royal-600/30 group-hover:scale-105 transition-transform">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
                    VerifyAI
                  </span>
                  <span className="bg-navy-800 text-slate-300 text-[9px] font-mono px-1.5 py-0.5 rounded border border-navy-700 hidden sm:inline">
                    SIH-26261
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 -mt-0.5 hidden sm:block">
                  AICTE Document & Regulatory Compliance
                </p>
              </div>
            </div>
          </div>

          {/* Right User Bar */}
          <div className="flex items-center gap-3 sm:gap-4">
            <button
              onClick={() => onNavigate && onNavigate('/verification-studio')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-royal-600 to-cyan-600 hover:from-royal-500 hover:to-cyan-500 text-white shadow-sm shadow-royal-900/30 transition-all border border-cyan-400/30"
              title="Launch AI Response Verification Studio & Benchmark"
            >
              <Zap className="w-3.5 h-3.5 text-cyan-200 fill-cyan-200" />
              <span className="hidden sm:inline">AI Studio & Benchmark</span>
              <span className="sm:hidden">Studio</span>
            </button>

            {user ? (
              <>
                <NotificationDropdown onNavigate={onNavigate} />

                <div className="h-6 w-px bg-navy-700 hidden sm:block"></div>

                <div className="flex items-center gap-3">
                  <div className="text-right hidden sm:block">
                    <div className="text-xs font-semibold text-slate-200">
                      {user.full_name}
                    </div>
                    <div className="mt-0.5">
                      {getRoleBadge(user.role)}
                    </div>
                  </div>

                  <div className="w-8 h-8 rounded-full bg-navy-700 border border-navy-600 flex items-center justify-center text-cyan-400 font-semibold text-xs">
                    {user.full_name ? user.full_name[0].toUpperCase() : <UserIcon className="w-4 h-4" />}
                  </div>

                  <button
                    onClick={onLogout}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-navy-800 transition-colors"
                    title="Sign Out"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onNavigate && onNavigate('/login')}
                  className="text-xs text-slate-200 hover:text-white px-3 py-1.5 rounded-lg font-medium hover:bg-navy-800 transition-colors"
                >
                  Sign In
                </button>
                <button
                  onClick={() => onNavigate && onNavigate('/login')}
                  className="text-xs bg-royal-600 hover:bg-royal-500 text-white px-3.5 py-1.5 rounded-lg font-semibold shadow-md shadow-royal-600/30 transition-colors"
                >
                  Launch Demo
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
