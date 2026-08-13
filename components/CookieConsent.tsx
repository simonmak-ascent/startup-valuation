"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "sv-cookie-consent";

export function CookieConsent() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    try {
      if (!localStorage.getItem(STORAGE_KEY)) setVisible(true);
    } catch {
      setVisible(true);
    }
  }, []);

  const accept = () => {
    try {
      localStorage.setItem(STORAGE_KEY, "accepted");
    } catch {
      // localStorage unavailable — ignore
    }
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 inset-x-0 z-50 p-4">
      <div className="max-w-[1100px] mx-auto card p-4 flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <p className="text-sm text-muted flex-1">
          We use an essential session cookie for sign-in and privacy-respecting analytics. See our{" "}
          <a href="/legal/cookies" className="text-brand hover:underline">
            Cookie Policy
          </a>
          .
        </p>
        <button onClick={accept} className="btn-brand whitespace-nowrap">
          Got it
        </button>
      </div>
    </div>
  );
}
