// Locale registry + landing copy for the startup-valuation frontage.
// Locales mirror the Ascent Partners site: en (default, no prefix), zh (/zh), hk (/hk).

export const locales = ["en", "zh", "hk"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "en";

export const LOCALE_META: Record<Locale, { htmlLang: string; label: string; prefix: string }> = {
  en: { htmlLang: "en-GB", label: "English", prefix: "" },
  zh: { htmlLang: "zh-Hans", label: "中文", prefix: "/zh" },
  hk: { htmlLang: "zh-Hant-HK", label: "繁體", prefix: "/hk" },
};

export function isLocale(value: string): value is Locale {
  return (locales as readonly string[]).includes(value);
}

export function hrefFor(locale: Locale, path: string): string {
  const clean = path === "/" ? "" : path.startsWith("/") ? path : `/${path}`;
  return `${LOCALE_META[locale].prefix}${clean}` || "/";
}

const ENDPOINT = "https://startup-valuation.ascent-partners.com/api";
const REGISTRY = "io.github.simonmak-ascent/startup-valuation";

export interface LandingCopy {
  type: string;
  name: string;
  value: string;
  thesis: string;
  stats: { value: string; label: string }[];
  capsHeading: string;
  capabilities: string[];
  connectHeading: string;
  connectIntro: string;
  factsHeading: string;
  facts: { label: string; value: string; code?: boolean }[];
  originHeading: string;
  originBody: string;
  techLink: string;
  contact: string;
  docs: string;
  source: string;
  back: string;
  copy: string;
  copied: string;
  crumbHome: string;
  crumbTools: string;
  langLabel: string;
}

export const LANDING_COPY: Record<Locale, LandingCopy> = {
  en: {
    type: "MCP server + REST API",
    name: "Startup Valuation",
    value: "Value pre-revenue and fast-growing startups with scorecard, VC and options methods.",
    thesis: "For a company with no revenue yet, the number is a forecast. We make the forecast explicit — and method-backed.",
    stats: [
      { value: "14", label: "MCP tools" },
      { value: "80+", label: "formulas" },
      { value: "5", label: "method families" },
      { value: "Open", label: "no API key" },
    ],
    capsHeading: "Capabilities",
    capabilities: [
      "14 tools / 80+ formulas",
      "Scorecard, Berkus, VC method, Black-Scholes, scenario analysis",
      "SaaS, biotech, fintech, marketplace, hardware",
      "Auditable: every result carries its formula, assumptions and steps",
    ],
    connectHeading: "Connect",
    connectIntro: "Point an MCP client at the hosted endpoint. Open access, no API key.",
    factsHeading: "Facts",
    facts: [
      { label: "Endpoint", value: ENDPOINT, code: true },
      { label: "Transport", value: "Streamable HTTP" },
      { label: "Auth", value: "Open — no API key" },
      { label: "Licence", value: "MIT" },
      { label: "Registry", value: REGISTRY, code: true },
    ],
    originHeading: "Where it comes from",
    originBody: "Built by the Ascent Partners technology practice from the Startup Valuation textbook — the method, opened for inspection.",
    techLink: "Technology Advisory",
    contact: "Contact us",
    docs: "Documentation",
    source: "Source",
    back: "All tools",
    copy: "Copy",
    copied: "Copied",
    crumbHome: "Home",
    crumbTools: "Open Tooling",
    langLabel: "Language",
  },
  zh: {
    type: "MCP 服务器 + REST API",
    name: "Startup Valuation",
    value: "以记分卡、风险投资及期权方法评估前期及高速增长的初创企业。",
    thesis: "对尚无收入的公司，这个数字是一个预测。我们让预测显性化，并有方法可依。",
    stats: [
      { value: "14", label: "个 MCP 工具" },
      { value: "80+", label: "个公式" },
      { value: "5", label: "类方法" },
      { value: "开放", label: "无需密钥" },
    ],
    capsHeading: "能力",
    capabilities: [
      "14 个工具 / 80+ 公式",
      "记分卡、Berkus、风险投资法、Black-Scholes、情景分析",
      "SaaS、生物科技、金融科技、平台、硬件",
      "可审计：每项结果附带其公式、假设与步骤",
    ],
    connectHeading: "连接",
    connectIntro: "将 MCP 客户端指向托管端点。开放访问，无需 API 密钥。",
    factsHeading: "信息",
    facts: [
      { label: "端点", value: ENDPOINT, code: true },
      { label: "传输", value: "Streamable HTTP" },
      { label: "认证", value: "开放——无需密钥" },
      { label: "许可", value: "MIT" },
      { label: "注册表", value: REGISTRY, code: true },
    ],
    originHeading: "来源",
    originBody: "由艾升集团技术咨询团队依据《初创企业估值》教材构建——将方法开放以供检视。",
    techLink: "技术咨询",
    contact: "联系我们",
    docs: "文档",
    source: "源代码",
    back: "全部工具",
    copy: "复制",
    copied: "已复制",
    crumbHome: "首页",
    crumbTools: "开放工具",
    langLabel: "语言",
  },
  hk: {
    type: "MCP 伺服器 + REST API",
    name: "Startup Valuation",
    value: "以記分卡、風險投資及期權方法評估前期及高速增長的初創企業。",
    thesis: "對尚無收入的公司，這個數字是一個預測。我們讓預測顯性化，並有方法可依。",
    stats: [
      { value: "14", label: "個 MCP 工具" },
      { value: "80+", label: "個公式" },
      { value: "5", label: "類方法" },
      { value: "開放", label: "無需密鑰" },
    ],
    capsHeading: "能力",
    capabilities: [
      "14 個工具 / 80+ 公式",
      "記分卡、Berkus、風險投資法、Black-Scholes、情景分析",
      "SaaS、生物科技、金融科技、平台、硬件",
      "可審計：每項結果附帶其公式、假設與步驟",
    ],
    connectHeading: "連接",
    connectIntro: "將 MCP 客戶端指向託管端點。開放存取，無需 API 密鑰。",
    factsHeading: "資訊",
    facts: [
      { label: "端點", value: ENDPOINT, code: true },
      { label: "傳輸", value: "Streamable HTTP" },
      { label: "認證", value: "開放——無需密鑰" },
      { label: "授權", value: "MIT" },
      { label: "註冊表", value: REGISTRY, code: true },
    ],
    originHeading: "來源",
    originBody: "由艾升集團技術諮詢團隊依據《初創企業估值》教材構建——將方法開放以供檢視。",
    techLink: "技術諮詢",
    contact: "聯絡我們",
    docs: "文件",
    source: "原始碼",
    back: "全部工具",
    copy: "複製",
    copied: "已複製",
    crumbHome: "首頁",
    crumbTools: "開放工具",
    langLabel: "語言",
  },
};

export interface ConnectClient {
  key: string;
  label: string;
  code: string;
}

export function connectClients(): ConnectClient[] {
  const key = "startup-valuation";
  const json = (o: unknown) => JSON.stringify(o, null, 2);
  const servers = json({ mcpServers: { [key]: { url: ENDPOINT } } });
  return [
    { key: "opencode", label: "OpenCode", code: json({ $schema: "https://opencode.ai/config.json", mcp: { [key]: { type: "remote", url: ENDPOINT } } }) },
    { key: "claude-code", label: "Claude Code", code: `claude mcp add --transport http ${key} ${ENDPOINT}` },
    { key: "claude-desktop", label: "Claude Desktop", code: servers },
    { key: "cursor", label: "Cursor", code: servers },
    { key: "vscode", label: "VS Code", code: json({ servers: { [key]: { type: "http", url: ENDPOINT } } }) },
    { key: "generic", label: "Any MCP client", code: servers },
  ];
}
