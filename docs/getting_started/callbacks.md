# Callbacks

Callbacks are HTTPS endpoints you register to receive asynchronous updates from DeltaPay.
Once a callback URL is registered for an account, DeltaPay automatically sends updates for all relevant events related to that account.

Currently, there are **two types of callbacks**:

1. [Instant Payment Notification (IPN)](../common_usecases/c2b.md#instant-payment-notification-ipn)
2. [Payment Request Status Updates](../common_usecases/c2b.md#payment-request-status-updates)


There is **no separate opt-in or opt-out** mechanism for specific callback types.
Once a callback is registered, both IPNs and Payment Request Updates will be sent as they occur.
You can choose to ignore those you do not need.

Each registered callback URL must be verified using its **public key**, which DeltaPay provides upon registration.
Different accounts require separate callback registrations and therefore separate key pairs — even if the actual callback URL is the same.
The public key used to verify both IPN and Payment Request callbacks is the same for a given registration.

All callbacks are sent **at least once**, meaning duplicates are possible.

> **Note:** Callback retries are not yet implemented. In future versions, DeltaPay will automatically retry failed deliveries up to three times if no valid acknowledgment is received.

## Callback Registration and Management

Users can register callbacks for a number of events that occur on the DeltaPay system.
To ensure easy extensibility, only the **base URL** is registered — DeltaPay automatically appends the relevant sub-path for each callback type.

For example, if the callback endpoint is:

```
https://api.client.co.sz
```

then:

* the IPN callback will be sent to `POST https://api.client.co.sz/transaction/ipn`
* the Payment Request update callback will be sent to `POST https://api.client.co.sz/payment-request/update`

### Account linkage and manager legal entity

Callbacks are registered **for a specific account**.
Any events pertaining to this account — such as transaction updates or payment request changes — are then communicated via the callback.

In some cases, a **third party** (e.g. an e-commerce platform or payment aggregator) may need to receive callbacks for accounts they do not directly own.
To support this, the registration includes a `manager_entity_id`, representing the **legal entity managing** the callback configuration.

This allows, for example, a marketplace platform to register and manage callbacks on behalf of merchants, while maintaining clear separation of permissions.

When retrieving callbacks registered for a specific account, the `view_callback_url` permission for the **manager entity** is sufficient if provided.

### Register callback

[`POST /account/callback-url/register`](https://api.dev.deltacrypt.net/docs#/accounts/register_callback_url_account_callback_url_register_post)

1. Registers the callback for the specified account.
2. Generates a new signing key pair. The public key is returned and must be used to verify callback signatures.

**Request Parameters**

* `callback_url`: *string* — The base URL to which DeltaPay will send callbacks
* `account_id`: *int* — The account for which the callback applies
* `manager_entity_id`: *int* — The legal entity responsible for managing the callback

**Required Permissions**

The caller must have the `set_callback_url` permission, either generally or specifically for the account **and** manager legal entity that the callback URL is set for.

**Example Response**

```json
{
  "callback_id": 4,
  "callback_url": "https://api.dev.deltacrypt.net",
  "account_id": 1004,
  "manager_entity_id": 1,
  "signing_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA57xXfRBtvwwotZBjW+zW\n7GzPchUlgzqJL5epFKL15E0gqgIu7O1fvnohpBdHe2uEAlGhJWw/LUsAKrYQECau\nm6gBEC6TWMzG8ne8yU5QH2lLq4J4BL4slHTSN//t7vejZu02N33STZP5CoS0bJ5f\nImk4s69jp5vjesUussFqBmVUHbEYn3D+Ihz/Hbrwx61EC0hRwBcTTYHCXgDEey3P\n0dztvs+WKP00qiUg8Eb16kaooA1/fI3ZaW94QnYYfH9UKspiJWtUfapdNExv1utD\ndOHZhdkbbtX8/JG3LZIyjUGrnxfDu0wC5RKWltBzKjzHn/b0Ai7xrElWfgjmRPtZ\nwQIDAQAB\n-----END PUBLIC KEY-----\n",
  "active": true,
  "deactivation_time": null
}
```

### Getting callbacks registered for an account

[`GET /account/callback-urls`](https://api.dev.deltacrypt.net/docs#/accounts/get_callback_urls_account_callback_urls_get)

**Request Parameters**

* `account_id`: *int* — The account whose registered callbacks should be returned
* `manager_entity_id`: *Optional[int]* — Optionally filter by managing entity

**Required Permissions**

The caller must have the `view_callback_url` permission, either generally or specifically for the account **and** manager legal entity.

**Example Response**

```json
{
  "callback_urls": [
    {
      "callback_id": 4,
      "callback_url": "https://api.dev.deltacrypt.net",
      "account_id": 42,
      "manager_entity_id": 1,
      "signing_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n",
      "active": true,
      "deactivation_time": null
    },
    {
      "callback_id": 1,
      "callback_url": "test",
      "account_id": 14,
      "manager_entity_id": 1,
      "signing_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n",
      "active": false,
      "deactivation_time": "2024-10-26T14:54:21.178337"
    }
  ]
}
```

### Deactivate callback

[`DELETE /account/callback-url/deactivate`](https://api.dev.deltacrypt.net/docs#/accounts/deactivate_callback_url_account_callback_url_deactivate_delete)

Sets the callback URL to inactive, preventing further callbacks for events related to this account.

**Request Parameters**

* `callback_id`: *int*

**Required Permissions**

The caller must have the `set_callback_url` permission, either generally or specifically for the account **and** manager legal entity.


## Verifying callbacks

To ensure the callback is authentic and has been sent by DeltaPay, you must verify the `signature` attribute included in each callback payload.
For code examples in common programming languages, see [Signature Verification](../common_usecases/signature_verification.md).


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
> If additional processing is required, handle it asynchronously (e.g. by queuing or background jobs) to avoid blocking the callback.