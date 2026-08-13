import { getDb } from "../client";
import { TABLES, type PaymentEvent, type Subscription } from "../schema";

/** Check if a Stripe event has already been processed (idempotency). */
export async function hasProcessedEvent(stripeEventId: string): Promise<boolean> {
  const db = await getDb();
  const [rows] = await db.query<[{ count: number }[]]>(
    `SELECT count() FROM ${TABLES.PAYMENT_EVENT} WHERE stripe_event_id = $id GROUP ALL`,
    { id: stripeEventId },
  );
  return (rows[0]?.count ?? 0) > 0;
}

/** Record a processed event (append-only ledger). */
export async function recordPaymentEvent(
  stripeEventId: string,
  type: string,
  payload: string,
): Promise<PaymentEvent> {
  const db = await getDb();
  const [rows] = await db.query<[PaymentEvent[]]>(
    `CREATE ${TABLES.PAYMENT_EVENT} CONTENT {
      stripe_event_id: $stripe_event_id,
      type: $type,
      payload: $payload,
      processed_at: time::now()
    } RETURN AFTER`,
    { stripe_event_id: stripeEventId, type, payload },
  );
  return rows[0]!;
}

/** Upsert a subscription by Stripe subscription id. */
export async function upsertSubscription(data: {
  userId: string;
  stripeSubscriptionId: string;
  stripeCustomerId: string;
  tier: string;
  status: string;
}): Promise<Subscription> {
  const db = await getDb();
  const [rows] = await db.query<[Subscription[]]>(
    `UPSERT ${TABLES.SUBSCRIPTION} SET
      user_id = $user_id,
      stripe_subscription_id = $stripe_subscription_id,
      stripe_customer_id = $stripe_customer_id,
      tier = $tier,
      status = $status,
      updated_at = time::now()
    RETURN AFTER`,
    {
      user_id: data.userId,
      stripe_subscription_id: data.stripeSubscriptionId,
      stripe_customer_id: data.stripeCustomerId,
      tier: data.tier,
      status: data.status,
    },
  );
  return rows[0]!;
}

export async function getSubscriptionForUser(userId: string): Promise<Subscription | null> {
  const db = await getDb();
  const [rows] = await db.query<[Subscription[]]>(
    `SELECT * FROM ${TABLES.SUBSCRIPTION} WHERE user_id = $user_id AND status = 'active' LIMIT 1`,
    { user_id: userId },
  );
  return rows[0] ?? null;
}
