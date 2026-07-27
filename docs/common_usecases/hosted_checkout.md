# Hosted Checkout

Hosted Checkout lets your platform (a WooCommerce plugin, a custom website, or any other e-commerce integration) accept DeltaPay payments without building the payment flow yourself. DeltaPay hosts the payment page — you create a session, redirect the customer to it, and read back the result.

At a high level: your server creates a checkout session and redirects the customer to a DeltaPay-hosted page. There the customer pays either by entering their DeltaPay phone number or username (and approving the payment request in the DeltaPay app) or by scanning the QR code shown on the page. The customer is then redirected back to your site, where you confirm the outcome with a single server-side call.

---

## Scenario

A customer on your online store clicks "Pay with DeltaPay" at checkout. The typical flow looks like this:

1. Your server creates a checkout session for the order, specifying the amount and your order reference, and receives back a `checkout_url`.
2. You redirect the customer's browser to the `checkout_url`.
3. On the DeltaPay-hosted page, the customer pays — either by entering their DeltaPay phone number or username and approving the payment request in the app, or by scanning the QR code shown on the page.
4. The customer is redirected back to your `return_url`.
5. Your server calls `verify-return` to confirm the outcome before marking the order as paid.

The only two calls you make are **create session** and **verify-return** — everything in between happens on the DeltaPay-hosted page. The rest of this document covers those two calls first, then the optional features.

---

## Setup

Before you can use Hosted Checkout, DeltaPay provisions an integration for your platform. You provide the following details and DeltaPay sets up the integration (and uploads your logo) for you:

- **Platform type** — `woocommerce` or `custom_website`
- **Allowed return domains** — the domains your `return_url` values may use (e.g. `myshop.co.sz`). This prevents open-redirect abuse.
- **Default return URL** — used if a session is created without one.
- **Accepted payer identifiers** *(optional)* — which identifiers customers may use to pay: phone number, username, or both. Defaults to both.
- **Display name** *(optional)* — what the checkout page shows as the merchant name. Defaults to your legal entity trading name.
- **Brand colour** *(optional)* — hex colour used on the checkout page.
- **Logo** *(optional)* — you supply the image; DeltaPay uploads it.
- **Retry limit** *(optional)* — the maximum number of payment attempts per session. Defaults to 3.

DeltaPay returns an **API key**. Keep it secret — it authenticates all your Hosted Checkout requests.

---

## Core flow

### 1. Create a session

[`POST /v1/hosted-checkout/sessions`](https://api.dev.deltacrypt.net/docs#/hosted_checkout/create_session_v1_hosted_checkout_sessions_post)

Call this from your server when the customer is ready to pay. Do not call it from the browser.

#### Request Parameters

- `amount`: *number* — Amount in SZL (e.g. `149.99`). Must be greater than 0.
- `merchant_reference`: *string* — Your internal order reference.
- `return_url`: *Optional[string]* — Where to redirect the customer after checkout. Must be on an allowed domain. Falls back to the integration's default if omitted.
- `platform_order_id`: *Optional[string]* — Your platform's order ID (e.g. WooCommerce order number).
- `display_description`: *Optional[string]* — Shown to the customer on the checkout page (e.g. `"Order #1042 at ACME Shop"`).
- `metadata`: *Optional[string]* — Free-form string stored on the session for your own use.
- `session_callback_url`: *Optional[string]* — A URL on your server that DeltaPay notifies when the session concludes. Must be on an allowed domain. See [Session callbacks](#session-callbacks).

**Authentication**: API key, passed as `x-api-key` in the request header. See [Authentication](../getting_started/authentication.md).

#### Example Request

```json
{
  "amount": 149.99,
  "merchant_reference": "ORDER-1042",
  "return_url": "https://myshop.co.sz/order/1042/thank-you",
  "display_description": "Order #1042 at ACME Shop"
}
```

#### Example Response

```json
{
  "checkout_session_id": "a3f2c891-4e10-4b2d-bc3a-1234567890ab",
  "checkout_url": "https://checkout.deltacrypt.net/hosted-checkout/?checkout_session_id=a3f2c891-4e10-4b2d-bc3a-1234567890ab",
  "expires_at": "2025-01-01T12:10:00Z"
}
```

Redirect the customer's browser to the returned `checkout_url`. Sessions expire **10 minutes** after creation; the checkout page shows a countdown.

### 2. Verify the result

[`GET /v1/hosted-checkout/sessions/{checkout_session_id}/verify-return`](https://api.dev.deltacrypt.net/docs#/hosted_checkout/verify_return_v1_hosted_checkout_sessions__checkout_session_id__verify_return_get)

When the customer returns to your `return_url`, call this from your server to get the authoritative outcome.

> **The redirect back to your site is not proof of payment.** A customer can close the tab, lose connectivity, or navigate to the `return_url` manually. `verify-return` is the single source of truth — always call it before fulfilling an order, and treat a `status` of `succeeded` as the only confirmation of payment. It is a read-only call and is safe to call more than once.

**Authentication**: API key (`x-api-key` header)

#### Example Response

```json
{
  "checkout_session_id": "a3f2c891-4e10-4b2d-bc3a-1234567890ab",
  "status": "succeeded",
  "merchant_reference": "ORDER-1042",
  "platform_order_id": null,
  "amount": 149.99,
  "finalised_at": "2025-01-01T12:04:33Z"
}
```

---

## Session status

| Status | Meaning |
|---|---|
| `pending` | Awaiting the customer's phone number or username. |
| `processing` | A payment request has been sent; waiting for the customer to approve it in the app. |
| `succeeded` | Payment received. |
| `failed` | All allowed attempts were exhausted without a successful payment. |
| `expired` | The session timed out before payment was completed. |
| `cancelled` | The session was cancelled. |

Only `succeeded` means the order has been paid.

---

## Redirects

There are two redirects in the flow:

1. **Into checkout** — after creating a session, you redirect the customer's browser to the `checkout_url`.
2. **Back to your site** — once the session concludes, the checkout page redirects the customer back to your `return_url`.

The `return_url` is either supplied per session or falls back to your integration's default. Either way it must be on one of your allowed return domains — this is validated when the session is created. The same applies to `session_callback_url`.

Because the return redirect is not proof of payment, confirm every order with [`verify-return`](#2-verify-the-result).

---

## Branding and logo

The checkout page is branded per integration with your display name, brand colour, and logo. You supply these during [setup](#setup) and DeltaPay configures them — there is no merchant-facing endpoint for branding; it is part of provisioning.

---

## Session callbacks

If you provide a `session_callback_url` when creating a session, DeltaPay sends a `POST` to that URL when the session concludes (`succeeded`, `failed`, `expired`, or `cancelled`). The body contains only the session id:

```json
{
  "checkout_session_id": "a3f2c891-4e10-4b2d-bc3a-1234567890ab"
}
```

The callback tells you *when* to check, not *what* the outcome was — respond with HTTP 200 and call [`verify-return`](#2-verify-the-result) for the authoritative result. Callbacks are best-effort, so treat them as an optimisation: even if one is missed, the customer's redirect to your `return_url` is a reliable trigger to verify.

---

## Retries

If a payment attempt fails (the customer rejected it, it timed out, or the identifier was wrong), the checkout page prompts the customer to try again. Your integration's retry limit sets the **maximum total number of attempts** per session (default: 3) — so a limit of 3 allows the first attempt plus two retries. Once the limit is reached, the session is marked `failed` and the customer is returned to your site.

---

## Upfront payer identifier

If you already know the customer's DeltaPay phone number or username at session creation (e.g. from a saved account), you can pass it upfront to skip the identifier-entry step on the checkout page.

#### Additional Request Parameters

- `payer_identifier_type`: *string* — `phone_number` or `username`
- `payer_identifier`: *string* — The phone number (E.164 format, e.g. `+26876123456`) or username.

```json
{
  "amount": 149.99,
  "merchant_reference": "ORDER-1042",
  "return_url": "https://myshop.co.sz/order/1042/thank-you",
  "payer_identifier_type": "phone_number",
  "payer_identifier": "+26876123456"
}
```

If the identifier is not found or is invalid, the session falls back to prompting the customer on the checkout page — the session-creation call itself does not fail.

---

## QR code payments

As an alternative to entering a phone number or username, the checkout page displays a QR code the customer can scan with the DeltaPay app to pay directly. Both paths settle the same session and produce the same outcome.

The QR code encodes the exact session amount and recipient. A QR payment must match the session amount exactly to settle it; a payment for a different amount is automatically reversed to the customer.

---

## Automatic duplicate payment reversal

If a customer pays twice for the same session (for example by scanning the QR code after already completing a payment request), DeltaPay automatically reverses the duplicate back to the customer. No action is required on your side, and only one payment is ever retained.
