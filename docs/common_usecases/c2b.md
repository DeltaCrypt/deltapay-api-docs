# Scenario

The customer pays for a service using DeltaPay. The service provider is notified of updates regarding the transaction, such as the success or failure of the payment.

For example, the process of paying for an item online might look like this:

### Using payment requests (recommended)

1. The website asks for the user's phone number or username used on DeltaPay. This information may also be linked to the user's profile.
2. The website sends a payment request to the user including at least the amount, recipient account, and reference (see [Payment Requests](payment_requests.md)). The website may optionally specify a timeout within which the payment request must be accepted.
3. The user either accepts or rejects the payment request. They can only accept requests where the resulting transaction would be possible.
4. Once the transaction settles, the IPN (Instant Payment Notification) is sent to the registered callback(s), notifying the seller of an update regarding the payment.

### Using QR codes

1. The website generates a payment QR code encoding the amount, recipient, and reference (see [QR Code Specification](qr_code.md)).
2. The user scans the QR code and the information is prefilled in the DeltaPay app.
3. The user approves and sends the transaction.
4. The IPN is sent to the registered callback(s), notifying the seller of an update regarding the payment.

> **Note:** We are working on supporting deep-links as an alternative to QR code or manual input.


## Payment reference

There are two options for encoding a payment reference:

* **notes**: can be entered and edited by the user (max 200 characters)
* **metadata**: is not shown to the user

Both are arbitrary strings that can be included in the QR code and will be picked up by the DeltaPay app.


<!-- # Callbacks

Callbacks are HTTPS endpoints you register to receive asynchronous updates from DeltaPay.
Once a callback URL is registered for an account, DeltaPay automatically sends updates for all relevant events related to that account.

Currently, there are **two types of callbacks**:

1. [Instant Payment Notification (IPN)](#instant-payment-notification-ipn) — transaction status updates
2. [Payment Request Status Updates](#payment-request-status-updates) — updates on pending payment requests

There is **no separate opt-in or opt-out** mechanism for specific callback types.
Once a callback is registered, both IPNs and Payment Request Updates will be sent as they occur.
You can choose to ignore those you do not need.

Each registered callback URL must be verified using its **public key**, which DeltaPay provides upon registration.
Different accounts require separate callback registrations and therefore separate key pairs — even if the actual callback URL is the same.
The public key used to verify both IPN and Payment Request callbacks is the same for a given registration.

All callbacks are sent **at least once** (duplicate delivery is possible).
Each event is retried up to three times if not acknowledged successfully (currently under implementation).
To handle duplicates, use the `transaction_id` or `payment_request_id` field as an idempotency key.

For information on how to register a callback URL, see the [setup](../getting_started/setup.md) section.


## Verifying callbacks

To ensure the callback is authentic and has been sent by DeltaPay, you must verify the `signature` attribute included in each callback payload.
For code examples in common programming languages, see [Signature Verification](signature_verification.md).


## Acknowledging callbacks

To confirm that your system has successfully received and processed a callback, your endpoint must return an **HTTP 200 OK** response.

If DeltaPay does not receive a `200` response (e.g. the request times out, returns another status code, or cannot be delivered),
the callback will be retried up to **three times** with exponential backoff.

After three failed attempts, the callback is considered **undeliverable**, and no further retries will be attempted.
There is currently no manual retry feature.

Example of a valid acknowledgment response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "received"}
```

> **Tip:** You should return the acknowledgment as quickly as possible.
> If additional processing is required, handle it asynchronously (e.g. by queuing or background jobs) to avoid blocking the callback. -->


# Instant Payment Notification (IPN)

The IPN callback is triggered for **all updates to transaction statuses** involving either the **sender** or **recipient account**. For more detailed information about callbacks, refer to 
[this section](../getting_started/callbacks.md).

**Callback URL format:**

```
base URL + /transaction/ipn
```

### Example payload

```json
{
  "transaction_id": 398,
  "transaction_type": "rent",
  "transaction_status": "succeeded",
  "initialisation_time": "2024-10-26T20:43:15.515122",
  "settled_time": "2024-10-26T20:43:21.639949",
  "note": "hello",
  "metadata": null,
  "source_of_funds": "",
  "bank_account": null,
  "sender_account_id": 1014,
  "sender_account_name": "New 3",
  "sender_name": "DeltaPay",
  "sender_till_name": null,
  "sender_phone_country_dialcode": null,
  "sender_phone_number": null,
  "recipient_account_id": 1001,
  "recipient_account_name": "Personal",
  "recipient_name": "adrian",
  "recipient_till_name": null,
  "recipient_phone_country_dialcode": null,
  "recipient_phone_number": null,
  "amount": 6,
  "cashback_received": 0,
  "cashback_spent": 0,
  "fee": 0,
  "commission_amount": 0,
  "signature": "VMDnRnvRJVvTHu9HNgjsIWhlXOd1bYkPPsp23y3cVl3Tn7Zzlg7AJAy5654fld5U7XrhQbDd3Mj684WcFnpbRgeiRIQDBtEL2eLKO7ZHjC/jg0n0zVjE2TRfPACuiXsmR/pJG+8hPmABBqThGj2hE5SEBFD4WSlzgAcLA0ZxZWvtDu2FAUpN1B+FtMfCmxa4DmH/GPtVs+80c8hHX3KGt35iaBrwD66vhdEUrSaYEgFooRmS3K9dm+neOPHgIfXG60sv03Ru5EZDMKNQvalUlCdLUerjr3eoZPs4DkYZj2FhwBZOJPBh6SDmCgSUsKclvepd0hExXNsRwOsKsxDcuQ=="
}
```

# Payment Request Status Updates

This callback is triggered whenever a **payment request status changes** for any request where the **recipient account** is the one associated with the registered callback. For more detailed information about callbacks, refer to 
[this section](../getting_started/callbacks.md).

**Callback URL format:**

```
base URL + /payment-request/update
```

### Example payload

```json
{
  "payment_request_id": 191,
  "payment_request_status": "rejected",
  "account_id": 14,
  "transaction_type": "eating_out",
  "transaction_id": null,
  "transaction_status": null,
  "till_name": null,
  "till_id": null,
  "note": "Peter ist ein netter Mensch",
  "metadata": null,
  "request_time": "2025-09-19T18:23:40.577917",
  "timeout": null,
  "sender_user_id": null,
  "sender_legal_entity_id": 2,
  "recipient_user_id": 76,
  "sender_name": "MinenhleGrocery",
  "recipient_name": "Sifiso Dlamini (@philipp20251)",
  "amount": 22,
  "signature": "iNUd7WxPOlYXdIsjwWi2MGHoYuAKwVvSl5TBQCXzduW5G0Wk8NYTffRuenJmh33Q3WW3sjDme4lfX376EmnHcynZMnN0IJDY0ZF6+KGQObWa22teeRw5RVBzuzosyY5rHzOz8w/JhZII8b/86qPLvYGcgfYU3eClbnJ3nAYdD5NxYDVFgAYo0/WrvqVgGsx+QVpa/ofY+ylkBpraiDGugPS4DOJM85Xl40fwCRq7QHbb8gLpYUFm4Ny6hR+iKr6TPrzIN54arQRjWbgOMSwHUv1QEAGfH+CW66RIkXgj8PqaUGYdtD57aXwa3Lo8IMaq1SJ/8chvaWV4I2rE3QsNPA=="
}
```

# Fallback mechanisms

Callbacks are the most efficient way to receive real-time updates, but they rely on your endpoint being continuously available.
If a callback cannot be delivered, it will currently **not be retried**.

In such cases, clients can use **polling** as a fallback:

* For transactions: use [`GET /full-transaction/from-id`](https://api.dev.deltacrypt.net/docs#/transactions/get_full_transaction_from_id_full_transaction_from_id_get) or [`GET /full-transaction/from-metadata`](https://api.dev.deltacrypt.net/docs#/transactions/get_full_transaction_from_metadata_full_transaction_from_metadata_get).
* For payment requests: use [`GET /payment-request/from-id`](https://api.dev.deltacrypt.net/docs#/payment_request/get_payment_request_from_id_payment_request_from_id_get) or [`GET payment-request/from-metadata`](https://api.dev.deltacrypt.net/docs#/payment_request/get_payment_request_from_metadata_payment_request_from_metadata_get).

This ensures that your system can recover state even if a callback was missed.