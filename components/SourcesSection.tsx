interface SourcesSectionProps {
  chapter: string;
  formulaNumber: string;
  libraryVersion: string;
  timestamp: string;
  gitCommit: string;
}

export function SourcesSection({
  chapter,
  formulaNumber,
  libraryVersion,
  timestamp,
  gitCommit,
}: SourcesSectionProps) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-text mb-3">Sources &amp; Traceability</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        <div className="flex items-start gap-2">
          <span className="text-brand shrink-0">📖</span>
          <div>
            <div className="font-medium text-text">Textbook Reference</div>
            <div className="text-muted">{chapter}</div>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <span className="text-brand shrink-0">📐</span>
          <div>
            <div className="font-medium text-text">Formula Number</div>
            <div className="text-muted">{formulaNumber}</div>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <span className="text-brand shrink-0">📦</span>
          <div>
            <div className="font-medium text-text">Library Version</div>
            <div className="text-muted">startup-valuation@{libraryVersion}</div>
          </div>
        </div>
        <div className="flex items-start gap-2">
          <span className="text-brand shrink-0">🕐</span>
          <div>
            <div className="font-medium text-text">Computed At</div>
            <div className="text-muted">{timestamp || "N/A"}</div>
          </div>
        </div>
        {gitCommit && (
          <div className="flex items-start gap-2 sm:col-span-2">
            <span className="text-brand shrink-0">🔗</span>
            <div>
              <div className="font-medium text-text">Source Commit</div>
              <div className="text-muted font-mono text-xs">
                <a
                  href={`https://github.com/simonplmak-cloud/startup-valuation/commit/${gitCommit}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-brand hover:underline"
                >
                  {gitCommit.slice(0, 7)}
                </a>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <div className="text-xs text-muted">
          All formulas are open source and auditable.{" "}
          <a
            href="https://github.com/simonplmak-cloud/startup-valuation"
            target="_blank"
            rel="noopener noreferrer"
            className="text-brand hover:underline"
          >
            View source code →
          </a>
        </div>
      </div>
    </div>
  );
}
