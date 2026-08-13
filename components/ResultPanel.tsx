import { formatCurrency } from "@/lib/utils";

interface ResultPanelProps {
  value: number;
  method: string;
  formulaNumber: string;
  auditStatus: string;
}

export function ResultPanel({ value, method, formulaNumber, auditStatus }: ResultPanelProps) {
  return (
    <div className="card bg-brand/5 border-brand/20">
      <div className="text-sm text-muted mb-1">
        Valuation Result — {method} ({formulaNumber})
      </div>
      <div className="text-[2.5rem] font-bold text-brand leading-tight">
        {formatCurrency(value)}
      </div>
      <div className="flex items-center gap-2 mt-3">
        <AuditBadge status={auditStatus} />
      </div>
    </div>
  );
}

function AuditBadge({ status }: { status: string }) {
  switch (status) {
    case "logged":
      return (
        <span className="inline-flex items-center gap-1 text-xs text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded-full">
          <span className="w-2 h-2 bg-green-500 rounded-full" />
          Audit logged
        </span>
      );
    case "failed":
      return (
        <span className="inline-flex items-center gap-1 text-xs text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
          <span className="w-2 h-2 bg-amber-500 rounded-full" />
          Audit unavailable
        </span>
      );
    case "skipped":
      return (
        <span className="inline-flex items-center gap-1 text-xs text-muted bg-gray-50 border border-gray-200 px-2 py-0.5 rounded-full">
          No audit trail
        </span>
      );
    default:
      return null;
  }
}
