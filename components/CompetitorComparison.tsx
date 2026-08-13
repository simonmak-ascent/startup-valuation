interface Competitor {
  name: string;
  price: string;
  methods: string;
  openSource: string;
  auditTrail: string;
  api: string;
}

const competitors: Competitor[] = [
  {
    name: "Startup Valuation Engine (us)",
    price: "Free",
    methods: "27 interactive + 60+ MCP tools",
    openSource: "✅ MIT — every formula auditable",
    auditTrail: "✅ SurrealDB immutable audit log",
    api: "✅ MCP + REST, no key required",
  },
  {
    name: "Equidam",
    price: "$49+/report",
    methods: "5 methods",
    openSource: "❌ Closed source",
    auditTrail: "❌ No audit trail",
    api: "Limited",
  },
  {
    name: "Carta (409A)",
    price: "$2,000+/valuation",
    methods: "1 method (409A)",
    openSource: "❌ Closed source",
    auditTrail: "IRS safe-harbor only",
    api: "Limited",
  },
  {
    name: "PitchBook",
    price: "$25,000+/year",
    methods: "Market data, no methodology",
    openSource: "❌ Closed source",
    auditTrail: "❌ No audit trail",
    api: "Enterprise only",
  },
  {
    name: "Kroll / Duff & Phelps",
    price: "$10,000+/engagement",
    methods: "Audit-grade, manual",
    openSource: "❌ Closed source",
    auditTrail: "Manual report",
    api: "None",
  },
];

const features: { label: string; key: keyof Competitor }[] = [
  { label: "Pricing", key: "price" },
  { label: "Methods", key: "methods" },
  { label: "Open Source", key: "openSource" },
  { label: "Audit Trail", key: "auditTrail" },
  { label: "API Access", key: "api" },
];

export function CompetitorComparison() {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b-2 border-border">
            <th className="text-left py-3 px-4 font-semibold text-text">Platform</th>
            {features.map((f) => (
              <th key={f.key} className="text-left py-3 px-4 font-semibold text-text">
                {f.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {competitors.map((c, i) => (
            <tr key={c.name} className={`border-b border-border ${i === 0 ? "bg-brand/5" : ""}`}>
              <td className={`py-3 px-4 ${i === 0 ? "font-semibold text-brand" : "text-text"}`}>
                {c.name}
              </td>
              {features.map((f) => (
                <td key={f.key} className="py-3 px-4 text-muted">
                  {c[f.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
