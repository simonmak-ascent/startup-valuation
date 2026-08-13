import Stripe from "stripe";

let stripeInstance: Stripe | null = null;

export function getStripe(): Stripe {
  if (!stripeInstance) {
    const apiKey = process.env.STRIPE_SECRET_KEY;
    if (!apiKey) {
      throw new Error("STRIPE_SECRET_KEY is not configured");
    }
    stripeInstance = new Stripe(apiKey);
  }
  return stripeInstance;
}

/**
 * Resolve the Stripe Price ID for a tier. Prices are read from Stripe Products
 * (never hardcoded), keyed by a `tier` metadata field on the Product.
 */
export async function getPriceIdForTier(tier: string): Promise<string> {
  const stripe = getStripe();
  const products = await stripe.products.list({ active: true });
  for (const product of products.data) {
    if (product.metadata.tier === tier) {
      const prices = await stripe.prices.list({ product: product.id, active: true, limit: 1 });
      const price = prices.data[0];
      if (price) return price.id;
    }
  }
  throw new Error(`No Stripe Price found for tier "${tier}"`);
}
