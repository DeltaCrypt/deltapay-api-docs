
# Eswatini Payment Switch (EPS)

<!-- TODO: Add section on switch specific limits, once we know them -->

The **EPS (Eswatini Payment Switch)** is the national payment infrastructure operated under the oversight of the Central Bank of Eswatini. It connects banks, mobile money providers, and other financial institutions into a single interoperable network.

### Why it matters

- **Interoperability:** Enables transfers across different institutions (banks, mobile wallets, and fintechs) instead of siloed systems.  
- **Real-time payments:** Supports near-instant transactions between participants.  
- **Standardisation:** Provides a common scheme, message formats, and rules for all integrations.  
- **Financial inclusion:** Expands reach by allowing users on different platforms to transact seamlessly.  
- **Regulatory backbone:** Acts as the core infrastructure for national payment flows under central bank governance.


### Access via DeltaPay APIs

The EPS is accessible directly through the existing DeltaPay APIs, meaning no separate integration, licensing, or onboarding onto the switch is required.

By integrating once with DeltaPay, you gain **all-in-one access** to the national payment network, allowing you to use your DeltaPay account to **collect from and disburse to any domestic institution** (banks, mobile money providers, and other licensed participants on the switch).

DeltaPay abstracts the complexity of the switch, handling connectivity, settlement, and collateral requirements, so you can focus purely on your product and user experience.

<!-- # EPS Overview -->

## EWLT vs ACCT:

The EPS distinguishes between two account schemes. **EWLT** (eWallet) refers to mobile money accounts, typically identified by phone-number-based formats. **ACCT** (Account) refers to traditional bank accounts, which follow institution-specific account numbering structures.  

#### Exception – DeltaPay:

While DeltaPay supports both account-based and wallet-based user models internally, all DeltaPay accounts are represented as **EWLT** on the switch.

## Current EPS Participants

The following table is based on the *Wallet and Account Guidelines* published by the Central Bank of Eswatini.

Within the context of the switch, participating institutions are referred to as **agents**. These agents include banks, mobile money providers, and other licensed financial institutions connected to the EPS.


| Institution                     | Code   | Scheme | Account Format Regex                  | Examples                                      |
|--------------------------------|--------|--------|----------------------------------------|-----------------------------------------------|
| Eswatini Bank                  | 103001 | ACCT   | 77[04]\d{8}                            | 77012345678, 77412345678                      |
| First National Bank            | 103002 | ACCT   | 5\d{10} \| 6[23]\d{9}                  | 51234567890, 62123456789, 63123456789         |
| Nedbank                        | 103003 | ACCT   | (1[12]99\|[2-8]000)\d{7}               | 1299123456, 119912345677, 80001234567         |
| Standard Bank                  | 103004 | ACCT   | 911\d{10}                              | 9111234567890, 9110101010101                  |
| Swaziland Building Society     | 203005 | ACCT   | 5\d{10}                                | 51234567890, 50101010101                      |
| Central Bank of Eswatini       | 103006 | ACCT   | unknown                                |                                               |
| Eswatini Mobile                | 203001 | EWLT   | ^79\d{6}$                              | 79123456                                      |
| Instacash                      | 203002 | EWLT   | ^7\d{7}$                               | 79123456, 76123456, 78123456                  |
| MTN Fintech                    | 203003 | EWLT   | 7[68]\d{6}                             | 76123456, 78123456                            |
| Standard Bank (Unayo)          | 203004 | ACCT   | ^455\d{10}$                            | 4551234567890, 4550101010101                  |
| Swaziland Building Society     | 203005 | EWLT   | ^7\d{7}$                               | 79123456, 76123456, 78123456                  |
| DeltaPay                       | 203006 | EWLT   | ^(?:7\d{7}\|\d{1,7})$                  | 79123456, 76123456, 78123456, 8789            |

>**Note**: Some institutions (*e.g.* SBS) support both ACCT and EWLT schemes under the same agent ID.

# Receiving from Switch Participants

## User Flow

A user initiates an EPS transfer (often referred to as a *fast transfer*) from their bank or mobile money platform to a DeltaPay account.

As with DeltaPay-to-DeltaPay transactions, incoming transactions and their status changes are delivered via the standard [IPNs](../common_usecases/c2b.md#instant-payment-notification-ipn), provided a callback is registered for the recipient account ID.

## Example IPN Payload (Incoming)

```json
{
    "transaction_id": 4200,
    "transaction_type": "eps_mint",
    "transaction_status": "succeeded",
    "initialisation_time": "2026-04-23T18:00:50.148951",
    "settled_time": "2026-04-23T18:05:51.786546",
    "note": "Order 69",
    "metadata": null,
    "source_of_funds": null,
    "bank_account": null,
    "sender_account_id": null,
    "sender_account_name": null,
    "sender_name": null,
    "sender_till_name": null,
    "sender_phone_country_dialcode": null,
    "sender_phone_number": null,
    "recipient_account_id": 58,
    "recipient_account_name": "Test",
    "recipient_name": "DeltaPay",
    "recipient_till_name": null,
    "recipient_phone_country_dialcode": null,
    "recipient_phone_number": null,
    "amount": 42,
    "cashback_received": 0,
    "cashback_spent": 0,
    "fee": 0,
    "commission_amount": 0,
    "direction": "in",
    "payment_request_id": null,
    "eps_debtor_account_id": "77012345678",
    "eps_debtor_name": null,
    "eps_debtor_account_scheme": "ACCT",
    "eps_instructing_agent_id": "103002",
    "eps_instructing_agent_name": "Eswatini Bank",
    "eps_creditor_account_id": "58",
    "eps_creditor_name": null,
    "eps_creditor_account_scheme": "EWLT",
    "eps_instructed_agent_id": "203006",
    "eps_instructed_agent_name": "DeltaPay",
    "promotion_data": null,
    "signature": "Ny2QULuN8cga2i0mnvE............."
}
```

## EPS-Specific Fields

For EPS transactions, additional fields are populated to reflect switch-level data:

| Field | Description |
|------|-------------|
| `eps_debtor_account_id` | The **sender’s account identifier** on the switch (i.e. the party initiating the payment). |
| `eps_debtor_name` | Name of the sender, if provided by the originating institution (often `null`). |
| `eps_debtor_account_scheme` | Scheme of the sender account (`EWLT` or `ACCT`). |
| `eps_instructing_agent_id` | The institution that **initiated the payment** on behalf of the sender (e.g. the sender’s bank or wallet provider). |
| `eps_instructing_agent_name` | Name of the institution that **initiated the payment** on behalf of the sender. |
| `eps_creditor_account_id` | The **recipient account identifier** on the switch (i.e. the intended destination of the funds). |
| `eps_creditor_name` | Name of the recipient, if provided (often `null`). |
| `eps_creditor_account_scheme` | Scheme of the recipient account (`EWLT` or `ACCT`). |
| `eps_instructed_agent_id` | The institution that **receives and processes the funds** on behalf of the recipient. |
| `eps_instructed_agent_name` | Name of the institution that **receives and processes the funds** on behalf of the recipient. |

### Mapping to DeltaPay Terminology

- **Debtor** &rarr; Sender  
- **Creditor** &rarr; Recipient  
- **Instructing Agent** &rarr; Sender’s institution (where the payment originates)  
- **Instructed Agent** &rarr; Recipient’s institution (where the payment is received)

The **payment reference** provided by the sender is mapped to the `note` field in DeltaPay.

## DeltaPay-Specific Behaviour (Incoming Payments)

For EPS transactions received by DeltaPay:
- **Debtor (sender)** is external
- **Creditor (recipient)** is always a DeltaPay account

- `eps_creditor_account_id` corresponds to the **DeltaPay account ID or phone number** that received the funds.
- The following fields are always set as:
    ```json
    eps_creditor_name: null
    eps_creditor_account_scheme: "EWLT"
    eps_instructed_agent_id: "203006"
    eps_instructed_agent_name: "DeltaPay"
    ```
- The `transaction_type` will always be `eps_mint`

Incoming EPS transactions can, therefore, be handled using the same logic as standard DeltaPay-to-DeltaPay transactions. On the DeltaPay side, the funds are credited to the recipient account and represented as `eps_mint` transactions.


## Payment References

The EPS currently does not support a native *Request to Pay* mechanism or structured metadata fields comparable to DeltaPay payment requests, as a result:

- There is no guaranteed way to attach structured metadata that will be returned with the transaction.
- Senders may optionally include a payment reference on their originating platform.

This reference is received by DeltaPay in the `note` field and can assist with reconciliation in addition to sender, amount, and timestamp matching.

For reconciliation and business logic, integrators should rely on:

- `transaction_status`
- `eps_debtor_account_id` (sender)
- `amount`
- `timestamp`
- `note` (payment reference, if provided)


# Sending to Switch participants

The general flow is very similar to the DeltaPay-to-DeltaPay disbursement flow.
Please read the section on [B2C disbursements]() first.

In particular:

1. (Optional) Check whether the transaction is possible using a [preview endpoint](#check--preview-eps-withdrawal)
2. Send and sign the transfer in a single call (recommended)
3. (Optional) Check the blockchain transaction status
4. Receive a callback when the transaction status changes (IPN)
5. Query the transaction on the DeltaPay side

As with DeltaPay-to-DeltaPay disbursements, there are two possible flows:

### Recommended flow

Use [`POST /transaction/eps-withdrawal`](https://api.dev.deltacrypt.net/docs#/transactions/eps_withdrawal_transaction_eps_withdrawal_post).

<!-- This endpoint: -->

<!-- * creates the DeltaPay transaction
* builds the underlying blockchain transaction
* signs it using the private key you provide
* submits it to the blockchain -->

The response contains a `tracking_id` corresponding to the `blockchain_transaction_id` of the transaction that was just created.

### Manual / raw-transaction flow (advanced)

If you cannot send the private key, you can use the raw-transaction flow:

1. Call [`POST /transaction/initiate-eps-withdrawal`](https://api.dev.deltacrypt.net/docs#/transactions/initiate_eps_withdrawal_transaction_initiate_eps_withdrawal_post) to obtain a `raw_transaction`
2. Sign it on your side
3. Submit the signed bytes using [`POST /blockchain/signed-transaction`](https://api.dev.deltacrypt.net/docs#/blockchain/send_signed_transaction_blockchain_signed_transaction_post)

This is only needed when your key-management requirements prevent you from using the recommended flow.
Details of signing and submitting raw transactions are described in the [blockchain section](blockchain.md).

## Check / Preview EPS Withdrawal

[`GET /transaction/eps-withdrawal-preview`](https://api.dev.deltacrypt.net/docs#/transactions/get_preview_eps_withdrawal_transaction_eps_withdrawal_preview_get) 


This endpoint is similar to [`GET /transaction/transfer-preview`](https://api.dev.deltacrypt.net/docs#/transactions/get_preview_transaction_transaction_transfer_preview_get), which is used to determine whether a DeltaPay-to-DeltaPay transfer will be possible.

It returns the information needed to decide whether an EPS withdrawal should be initiated, without creating a transaction.

In addition to the checks performed on the DeltaPay side, this endpoint also uses the EPS to check whether the recipient account on the switch is active.

This does **not** guarantee that the transaction will succeed. The preview only checks whether the target account is active on the EPS; it does not validate other constraints such as transaction or account limits. The same race conditions that apply to standard transfer previews also apply here.

<!-- Note that this is **not a guarantee** that the transaction will be successful. It only checks whether an account on the EPS is active, but no other constraints such as limits that may be acceeded by the transaction. The same race conditions apply as with standard transfer previews. -->


**Request Parameters**

* `sender_wallet_address`: *string*
* `amount`: *number*
* `instructed_agent_id`: *string*
* `creditor_account_id`: *string*
* `creditor_account_scheme`: *string (`EWLT` or `ACCT`)*


The `sender_wallet_address` must be [linked](../getting_started/setup.md#link-api-key) to an account.

The `instructed_agent_id` identifies the switch participant to which the funds are sent. The `creditor_account_id` is typically an account number or phone number, depending on the receiving institution. Refer to the [participant table](#current-eps-participants) for institution-specific account formats.


<!-- TODO: maybe just make this bold -->
### Response structure
<!-- **Response structure** -->

The endpoint always returns the same top-level fields:

* `transaction_possible`
* `fee_info`

What changes is which of these contain data:

* `transaction_possible.possible` is always present.

  * If *true*, it includes `sender_account_id`.
  * If *false*, it includes `error_name` and `error_arguments` describing why the transfer cannot proceed.
* `fee_info` is populated when the fee can be calculated. It is `null` if the transaction is not possible.

This allows you to determine whether to proceed and present meaningful feedback to the user before actually creating a transaction.

**Example response structure (transaction possible):**

```json
{
  "transaction_possible": {
    "possible": true,
    "sender_account_id": 26,
    "fee": 0.0
  },
  "fee_info": {
    "fee": 0.0,
    "cashback_received": null
  }
}
```

**Example response structure (transaction not possible):**

```json
{
  "transaction_possible": {
    "possible": false,
    "error_name": "EPS_CREDITOR_ACCOUNT_VALIDATION_FAILED",
    "error_arguments": [
      "AC03",
      "AC03:WALLET_ACCOUNT_NUMBER_NOT_FOUND",
      "203005",
      "26812345678",
      "EWLT"
    ]
  },
  "fee_info": null
}
```

## Send and Sign Transaction (Recommended Flow)

For most server-side integrations, you should use:

[`POST /transaction/eps-withdrawal`](https://api.dev.deltacrypt.net/docs#/transactions/eps_withdrawal_transaction_eps_withdrawal_post)

This endpoint:

1. Validates the request and applies basic checks
2. Creates the DeltaPay transaction
3. Constructs the underlying raw blockchain transaction
4. Signs it using the provided private key
5. Submits it to the blockchain
6. Submits the corresponding request to the EPS
7. Returns a **tracking ID**  that can be used to correlate callbacks and queries

<!-- TODO: be consistant with formatting -->
<!-- ### Request Parameters -->
**Request Parameters**

<!-- TODO: Update once we fixed phone_number, username, account_id thing -->
<!-- TODO: most likely to be added:
* `recipient_till_id`: *Optional[int]*
* `recipient_account_id`: *Optional[int]* (or business)
* `recipient_username`: *Optional[string]* -->
The body closely mirrors [`POST /transaction/initiate-eps-withdrawal`](https://api.dev.deltacrypt.net/docs#/transactions/initiate_eps_withdrawal_transaction_initiate_eps_withdrawal_post), except it replaces the `sender_wallet_address` with the `private_key` field.

* `private_key`: *string*
* `amount`: *number*
* `note`: *Optional[string]*
* `metadata`: *Optional[string]*
* `instructed_agent_id`: *string*,
* `creditor_account_id`: *string*,
* `creditor_account_scheme`: *string (`EWLT` or `ACCT`)*

As for similar endpoints:

* The `private_key` must be [linked](../getting_started/setup.md#link-api-key) to an account.
* The `metadata` is an optional free-form string (e.g., JSON-encoded string with order info).

<!-- ### Example Response -->
**Example Response**

```json
{
  "success": true,
  "tracking_id": "420"
}
```

The `tracking_id` corresponding to the `blockchain_transaction_id` of the transaction that was just created and can be used to poll its status, see [Get Blockchain Transaction Status](blockchain.md#get-blockchain-transaction-status).


>**Note**: The manual flow follows the same principles as other raw transaction flows described in the blockchain section.

## Example Payload (Outgoing)

```json
{
    "transaction_id": 10000,
    "transaction_type": "eps_withdrawal",
    "transaction_status": "approved",
    "initialisation_time": "2026-04-22T18:00:50.148951",
    "settled_time": null,
    "note": "Rent for uncle Tom",
    "metadata": null,
    "source_of_funds": null,
    "bank_account": null,
    "sender_account_id": 58,
    "sender_account_name": "Test",
    "sender_name": "DeltaPay",
    "sender_till_name": null,
    "sender_phone_country_dialcode": null,
    "sender_phone_number": null,
    "recipient_account_id": null,
    "recipient_account_name": null,
    "recipient_name": "n/a",
    "recipient_till_name": null,
    "recipient_phone_country_dialcode": null,
    "recipient_phone_number": null,
    "amount": 42,
    "cashback_received": 0,
    "cashback_spent": 0,
    "fee": 10,
    "commission_amount": 0,
    "direction": "out",
    "payment_request_id": null,
    "eps_debtor_account_id": "58",
    "eps_debtor_name": null,
    "eps_debtor_account_scheme": "EWLT",
    "eps_instructing_agent_id": "203006",
    "eps_instructing_agent_name": "DeltaPay",
    "eps_creditor_account_id": "51234567890",
    "eps_creditor_name": null,
    "eps_creditor_account_scheme": "ACCT",
    "eps_instructed_agent_id": "1003002",
    "eps_instructed_agent_name": "First National Bank",
    "promotion_data": null,
    "signature": "E4hLq13GRblPnJ............."
}
```