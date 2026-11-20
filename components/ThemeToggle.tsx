"use client";

import { useEffect, useState } from "react";

const KEY = "apg-theme";

const DEFAULT_LABELS = { toLight: "Switch to light mode", toDark: "Switch to dark mode" };

/**
 * Dark/light switch — APG parity (data-theme + localStorage["apg-theme"]).
 *
 * Its accessible name is chrome: on `/zh` and `/hk` a screen reader was announcing English, the one
 * place the localised shell left untranslated because it is not visible text.
 */
export function ThemeToggle({ labels = DEFAULT_LABELS }: { labels?: { toLight: string; toDark: string } } = {}) {
  const [dark, setDark] = useState(true);

  useEffect(() => {
    setDark(document.documentElement.getAttribute("data-theme") !== "light");
  }, []);

  function toggle() {
    const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem(KEY, next);
    } catch {
      /* ignore */
    }
    setDark(next === "dark");
  }

  return (
    <button
      type="button"
      className="theme-toggle ms-auto"
      aria-label={dark ? labels.toLight : labels.toDark}
      title={dark ? labels.toLight : labels.toDark}
      onClick={toggle}
    >
      <span aria-hidden="true">◐</span>
    </button>
  );
}
