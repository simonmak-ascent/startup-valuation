import katex from "katex";

export function renderLatex(formula: string, displayMode = false): string {
  try {
    return katex.renderToString(formula, {
      throwOnError: false,
      displayMode,
      strict: false,
    });
  } catch {
    return formula;
  }
}

export function renderLatexInline(formula: string): string {
  return renderLatex(formula, false);
}

export function renderLatexBlock(formula: string): string {
  return renderLatex(formula, true);
}
