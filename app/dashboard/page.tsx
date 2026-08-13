import { redirect } from "next/navigation";
import Link from "next/link";
import { auth } from "@/lib/auth/config";
import { getAuditLogsForUser } from "@/lib/db/repositories/audit";
import { getSubscriptionForUser } from "@/lib/db/repositories/billing";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const session = await auth();
  if (!session?.user?.id) {
    redirect("/sign-in");
  }

  let subscription = null;
  try {
    subscription = await getSubscriptionForUser(session.user.id);
  } catch {
    subscription = null;
  }

  const isPro = subscription?.tier === "pro" || subscription?.tier === "enterprise";

  let runs: Awaited<ReturnType<typeof getAuditLogsForUser>> = [];
  if (isPro) {
    try {
      runs = await getAuditLogsForUser(session.user.id);
    } catch {
      runs = [];
    }
  }

  return (
    <div className="section max-w-[900px]">
      <h1 className="text-3xl font-bold text-text mb-2">Dashboard</h1>
      <p className="text-muted mb-8">
        Signed in as {session.user.email}. Tier: {subscription?.tier ?? "free"}.
      </p>

      {!isPro ? (
        <div className="card text-center py-12">
          <h2 className="text-xl font-semibold mb-3">Upgrade to Pro</h2>
          <p className="text-muted mb-6">
            Export auditable PDF reports of your valuation runs with full formula traceability. The
            free calculators stay free.
          </p>
          <Link href="/api/billing/checkout" className="btn-brand">
            Upgrade to Pro
          </Link>
        </div>
      ) : runs.length === 0 ? (
        <div className="card text-center py-12">
          <h2 className="text-xl font-semibold mb-3">No valuation runs yet</h2>
          <p className="text-muted mb-6">Run a calculator to start building your audit history.</p>
          <Link href="/" className="btn-brand">
            Try a calculator
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {runs.map((run) => (
            <div key={run.id} className="card flex items-center justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-text">{run.method}</div>
                <div className="text-muted text-sm">
                  {run.result} · {run.formula_number} · {run.created_at?.slice(0, 10)}
                </div>
              </div>
              <Link
                href={`/api/export/report?run_id=${encodeURIComponent(run.id)}`}
                className="btn-brand"
              >
                Export report
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
