"use client";

import { useEffect, useState } from "react";

const KEY = "apg-theme";

/** Dark/light switch — APG parity (data-theme + localStorage["apg-theme"]). */
export function ThemeToggle() {
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
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      title={dark ? "Switch to light mode" : "Switch to dark mode"}
      onClick={toggle}
    >
      <span aria-hidden="true">◐</span>
    </button>
  );
}
