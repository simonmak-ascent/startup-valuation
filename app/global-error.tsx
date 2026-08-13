"use client";

import { useEffect } from "react";
import * as Sentry from "@sentry/nextjs";

export default function GlobalError({
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
    <html lang="en">
      <body className="antialiased" style={{ background: "#f8fafc" }}>
        <div className="min-h-screen flex items-center justify-center px-4">
          <div className="max-w-md w-full p-8 text-center rounded-xl bg-white border border-[#e2e8f0]">
            <h1 className="text-2xl font-bold mb-3" style={{ color: "#1e293b" }}>
              Something went wrong
            </h1>
            <p className="mb-6" style={{ color: "#64748b" }}>
              An unexpected error occurred. Please try again.
            </p>
            <button
              onClick={reset}
              className="px-6 py-3 rounded-lg font-semibold text-white cursor-pointer"
              style={{ background: "#0083AB" }}
            >
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
