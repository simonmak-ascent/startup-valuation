"use client";

import { useEffect } from "react";
import * as Sentry from "@sentry/nextjs";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center bg-bg px-4">
      <div className="card max-w-md w-full p-8 text-center">
        <h1 className="text-2xl font-bold text-text mb-3">Something went wrong</h1>
        <p className="text-muted mb-6">An unexpected error occurred. Please try again.</p>
        <button onClick={reset} className="btn-brand">
          Try again
        </button>
      </div>
    </div>
  );
}
