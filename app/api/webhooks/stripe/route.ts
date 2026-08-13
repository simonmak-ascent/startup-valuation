import { NextResponse } from "next/server";
import { getStripe } from "@/lib/billing/stripe";
import {
  hasProcessedEvent,
  recordPaymentEvent,
  upsertSubscription,
} from "@/lib/db/repositories/billing";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const signature = request.headers.get("stripe-signature");
  const secret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!signature || !secret) {
    return NextResponse.json({ error: "INVALID_SIGNATURE" }, { status: 400 });
  }

  const rawBody = await request.text();

  let event;
  try {
    const stripe = getStripe();
    event = stripe.webhooks.constructEvent(rawBody, signature, secret);
  } catch {
    return NextResponse.json({ error: "INVALID_SIGNATURE" }, { status: 400 });
  }

  // Idempotency: skip if this event was already processed (AC-E2).
  if (await hasProcessedEvent(event.id)) {
    return NextResponse.json({ received: true, duplicate: true });
  }

  // Process known events.
  if (event.type === "checkout.session.completed") {
    const session = event.data.object as {
      subscription?: string;
      customer?: string;
      metadata?: { user_id?: string; tier?: string };
    };
    const userId = session.metadata?.user_id;
    const tier = session.metadata?.tier ?? "pro";
    if (userId && session.subscription && session.customer) {
      await upsertSubscription({
        userId,
        stripeSubscriptionId: session.subscription as string,
        stripeCustomerId: session.customer as string,
        tier,
        status: "active",
      });
    }
  } else if (
    event.type === "customer.subscription.updated" ||
    event.type === "customer.subscription.deleted"
  ) {
    const sub = event.data.object as { id: string; status: string; customer?: string };
    const stripe = getStripe();
    const customerId = typeof sub.customer === "string" ? sub.customer : sub.customer?.id;
    if (customerId) {
      const customer = await stripe.customers.retrieve(customerId);
      const userId = (customer as { metadata?: { user_id?: string } }).metadata?.user_id;
      if (userId) {
        await upsertSubscription({
          userId,
          stripeSubscriptionId: sub.id,
          stripeCustomerId: customerId,
          tier: "pro",
          status: sub.status,
        });
      }
    }
  }

  // Record the event last (append-only idempotency ledger).
  await recordPaymentEvent(event.id, event.type, rawBody);

  return NextResponse.json({ received: true });
}
