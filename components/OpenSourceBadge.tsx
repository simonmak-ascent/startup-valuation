"use client";

import { useEffect, useState } from "react";

const REPO = "simonplmak-cloud/startup-valuation";

interface OpenSourceBadgeProps {
  showStars?: boolean;
  compact?: boolean;
}

export function OpenSourceBadge({ showStars = true, compact = false }: OpenSourceBadgeProps) {
  const [stars, setStars] = useState<number | null>(null);

  useEffect(() => {
    if (!showStars) return;
    fetch(`https://api.github.com/repos/${REPO}`)
      .then((r) => r.json())
      .then((d) => {
        if (typeof d.stargazers_count === "number") setStars(d.stargazers_count);
      })
      .catch(() => {});
  }, [showStars]);

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border font-semibold ${
        compact ? "px-2.5 py-0.5 text-xs" : "px-4 py-1.5 text-sm"
      } bg-green-50 text-green-700 border-green-200`}
    >
      <svg
        className="w-4 h-4"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle cx="12" cy="12" r="9" />
        <path d="M12 3v18M3 12h18" opacity="0" />
        <path d="M8 12l-2-2M16 12l2-2M12 9a3 3 0 0 0-3 3" opacity="0" />
      </svg>
      Open Source · MIT
      {showStars && stars !== null && (
        <span className="inline-flex items-center gap-1 ml-1">
          <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z" />
          </svg>
          {stars.toLocaleString()}
        </span>
      )}
    </div>
  );
}
