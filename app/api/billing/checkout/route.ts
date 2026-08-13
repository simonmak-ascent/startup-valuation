import { NextResponse } from "next/server";
import { auth } from "@/lib/auth/config";
import { getStripe, getPriceIdForTier } from "@/lib/billing/stripe";

export const dynamic = "force-dynamic";

const VALID_TIERS = ["pro", "enterprise"];

export async function POST(request: Request) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json(
      { error: "UNAUTHORIZED", message: "Sign in required" },
      { status: 401 },
    );
  }

  let tier: string;
  try {
    const body = (await request.json()) as { tier?: string };
    tier = body.tier ?? "";
  } catch {
    return NextResponse.json(
      { error: "VALIDATION_ERROR", message: "Invalid JSON" },
      { status: 400 },
    );
  }

  if (!VALID_TIERS.includes(tier)) {
    return NextResponse.json(
      { error: "INVALID_TIER", message: "tier must be pro or enterprise" },
      { status: 400 },
    );
  }

  try {
    const stripe = getStripe();
    const priceId = await getPriceIdForTier(tier);

    const checkout = await stripe.checkout.sessions.create({
      mode: "subscription",
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${process.env.NEXT_PUBLIC_BASE_URL ?? "https://startup-valuation.simonmak.com"}/dashboard?checkout=success`,
      cancel_url: `${process.env.NEXT_PUBLIC_BASE_URL ?? "https://startup-valuation.simonmak.com"}/?checkout=cancelled`,
      metadata: { user_id: session.user.id, tier },
    });

    return NextResponse.json({ url: checkout.url });
  } catch (e) {
    return NextResponse.json(
      { error: "CHECKOUT_FAILED", message: (e as Error).message },
      { status: 500 },
    );
  }
}
