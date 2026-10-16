import Stripe from "stripe";
export const stripe = new Stripe("chave-ficticia");
export async function assinar(plano: string) {
  return stripe.checkout.sessions.create({ mode: "subscription", line_items: [{ price: plano, quantity: 1 }] });
}
