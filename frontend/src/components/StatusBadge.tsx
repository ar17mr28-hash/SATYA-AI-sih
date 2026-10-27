import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = (status || '').toLowerCase().replace(/\s+/g, '_');
  
  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-300';
  let label = status.replace(/_/g, ' ').toUpperCase();

  switch (norm) {
    case 'approved':
    case 'mark_complete_approved':
      colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-300 ring-1 ring-emerald-500/20';
      label = 'APPROVED';
      break;
    case 'under_review':
    case 'submitted':
      colorClasses = 'bg-blue-50 text-blue-700 border-blue-300 ring-1 ring-blue-500/20';
      label = 'UNDER REVIEW';
      break;
    case 'clarification_requested':
      colorClasses = 'bg-amber-50 text-amber-700 border-amber-300 ring-1 ring-amber-500/20';
      label = 'CLARIFICATION REQ.';
      break;
    case 'correction_requested':
      colorClasses = 'bg-orange-50 text-orange-700 border-orange-300 ring-1 ring-orange-500/20';
      label = 'CORRECTION REQ.';
      break;
    case 'rejected':
    case 'reject_application':
      colorClasses = 'bg-red-50 text-red-700 border-red-300 ring-1 ring-red-500/20';
      label = 'REJECTED';
      break;
    case 'draft':
      colorClasses = 'bg-slate-100 text-slate-600 border-slate-300';
      label = 'DRAFT';
      break;
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-semibold';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border tracking-wide uppercase font-mono ${sizeClasses} ${colorClasses}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
      {label}
    </span>
  );
};

export const RiskBadge: React.FC<{ risk: string }> = ({ risk }) => {
  const r = (risk || '').toLowerCase();
  let bg = 'bg-slate-100 text-slate-700 border-slate-200';
  if (r === 'low') bg = 'bg-emerald-50 text-emerald-700 border-emerald-300';
  else if (r === 'medium') bg = 'bg-amber-50 text-amber-700 border-amber-300';
  else if (r === 'high') bg = 'bg-red-50 text-red-700 border-red-300 font-bold';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs border uppercase tracking-wider font-mono ${bg}`}>
      {r} RISK
    </span>
  );
};
