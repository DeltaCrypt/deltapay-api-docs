# Scenario

Disbursing funds to a customer’s (or another business’) DeltaPay account follows this process:

1. (Optional) Check whether the transaction is possible using a [preview endpoint](#1-check--preview-transaction)
2. Send and sign the transfer in a single call (recommended)
3. (Optional) Check the blockchain transaction status
4. Receive a callback when the transaction status changes (IPN)
5. Query the transaction on the DeltaPay side

### Recommended flow

Use `POST /transaction/send-transfer`.
This endpoint:

* creates the DeltaPay transaction
* builds the underlying blockchain transaction
* signs it using the private key you provide
* submits it to the blockchain

The response contains a `tracking_id` corresponding to the `blockchain_transaction_id` of the transaction that was just created.

### Manual / raw-transaction flow (advanced)

If you cannot send the private key, you can use the raw-transaction flow:

1. Call `POST /transaction/initiate-transfer` to obtain a `raw_transaction`
2. Sign it on your side
3. Submit the signed bytes using `POST /blockchain/signed-transaction`

This is only needed when your key-management requirements prevent you from using the recommended flow.
Details of signing and submitting raw transactions are described in the [blockchain section](blockchain.md).


### Is it Safe to Send the Private Key?

In the recommended flow, the private key is included in the HTTPS request body. The following points describe how the key is handled on DeltaPay’s side:

* Transport uses TLS, so the private key is protected by the same communication channel that is normally used to send API keys, passwords, and other sensitive credentials.
* The key is used only to sign the transaction in memory and is not stored in DeltaPay’s database or logs.
* Requests should be made from your backend system. The private key should not be exposed to client-side environments.
* The private key should be treated like any other sensitive secret on your side (for example, avoid logging it and keep it in a secret-management system).

Using this flow effectively shifts the security boundary from the public–private key pair itself to the security of the channel and environment through which the private key is transmitted. This is the same model used when sending API keys, authentication tokens, or passwords to a backend service.

If your policies do not allow the private key to leave your infrastructure, use the manual flow.


## Transactions vs Blockchain Transactions

DeltaPay distinguishes between:

**DeltaPay transactions (platform-level)**

  * Represent **business events** like transfers, deposits, withdrawals
  * Stored in the DeltaPay database with a `transaction_id` and business-level status (pending, initiated, approved, failed, succeeded, and reversed)

**Blockchain transactions (on-chain)**

  * Ethereum transactions that interact with smart contracts on our permissioned chain
  * Identified by a `blockchain_transaction_id` and have their own status (pending, failed, and succeeded)

A **single** DeltaPay transaction may involve **multiple** blockchain transactions (for example: initiate, approve, and finalise).

When a blockchain transaction fails, the underlying error comes directly from the smart contract. These errors are per blockchain transaction, not per DeltaPay transaction. If you want to understand exactly *why* something failed on-chain, you can inspect the blockchain error using:

* [`GET /blockchain/transaction-status`](https://api.dev.deltacrypt.net/docs#/blockchain/get_transaction_status_blockchain_transaction_status_get)
* [`GET /blockchain/transaction/error-message`](https://api.dev.deltacrypt.net/docs#/blockchain/get_transaction_error_message_blockchain_transaction_error_message_get)

This information is primarily useful for debugging or for communicating more detailed error context to the end user. In normal operation, the [**preview endpoints**](#1-check--preview-transaction) should prevent the vast majority of attempts that would result in an on-chain failure.
The blockchain error endpoints are therefore mostly relevant for edge cases, such as race conditions (e.g. limits or balances changing after the preview call). For more information on how to interact with the blockchain, please refer to [this section](blockchain.md).


Here’s a version updated to use `transfer-preview`, with your new examples and a short explanation of the response shape.


# Check / Preview Transaction

Before sending money, it is advisable to preview whether the transaction is likely to succeed. This avoids unnecessary polling and simplifies error handling.

A transaction may fail for several reasons:

- Insufficient account balance
- Limits exceeded (daily / monthly / wallet-level)
- Transaction amount too low
- Account suspended or closed
- User not whitelisted

> **Note**: Insufficient spending allowances (daily spending limits) do not prevent the transaction from being created. In such cases the transaction will be created but **require approval**, which is reflected in its status when you query it or receive callbacks.

## Transfer preview

[`GET /transaction/transfer-preview`](https://api.dev.deltacrypt.net/docs#/transactions/get_transfer_preview_transaction_transfer_preview_get)

This endpoint returns all information needed to decide whether a transfer should be initiated, without actually creating a transaction.

**Request Parameters**

* `sender_wallet_address`: *string*
* `transaction_type`: *string*
* `amount`: *number*
* `recipient_phone_country_dialcode`: *Optional[string]*
* `recipient_phone_number`: *Optional[string]*
* `recipient_username`: *Optional[string]*
* `recipient_business_account_id`: *Optional[int]*


The `sender_wallet_address` must be [linked](../getting_started/setup.md#link-api-key) to an account.

The recipient can be identified using (`recipient_phone_country_dialcode` + `recipient_phone_number`), `recipient_username`, **or** a `recipient_business_account_id`. For personal accounts, use either the phone number or the username; for business accounts, use the business account ID.

<!-- TODO: maybe just make this bold -->
### Response structure
<!-- **Response structure** -->

The endpoint always returns the same top-level fields:

* `transaction_possible`
* `fee_info`
* `cashback_possible`
* `recipient_username`
* `recipient_legal_name`
* `recipient_business_account_info`
* `sender_tills`
* `recipient_tills`

What changes is which of these contain data:

* `transaction_possible.possible` is always present.

  * If *true*, it includes `sender_account_id`.
  * If *false*, it includes `error_name` and `error_arguments` describing why the transfer cannot proceed.
* `fee_info` is populated when the fee can be calculated. It is `null` if the transaction is not possible.
* `cashback_possible` describes whether cashback can be applied and, if not, why. It is `null` when cashback is not evaluated (for example, when the transaction itself is not possible). <!-- TODO: this may change depending on how we end up doing cashback transaction. -->
* Recipient fields and tills arrays are filled when the recipient and available tills can be resolved; otherwise they are `null` or empty arrays.

This gives you enough information to decide whether to proceed and to show meaningful messages to the user before actually creating a transaction.

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
  },
  "cashback_possible": {
    "possible": false,
    "error_name": "ERR_ACCOUNT_TYPE_REQUIRED",
    "error_arguments": [
      "83",
      "['3']",
      "1"
    ]
  },
  "recipient_username": "dayni",
  "recipient_legal_name": "D. Test",
  "recipient_business_account_info": null,
  "sender_tills": [
    {
      "till_name": "mulatill",
      "till_id": 40,
      "active": true,
      "deactivation_time": null
    }
  ],
  "recipient_tills": []
}
```

**Example response structure (transaction not possible):**

```json
{
  "transaction_possible": {
    "possible": false,
    "error_name": "Sender wallet address does not belong to an active account or user",
    "error_arguments": [
      "0xe1a5e0d853a2620ffac9d15fe9e5fd8d19370ca6"
    ]
  },
  "fee_info": null,
  "cashback_possible": null,
  "recipient_username": null,
  "recipient_legal_name": null,
  "recipient_business_account_info": null,
  "sender_tills": [],
  "recipient_tills": []
}
```


### Race Conditions and Limitations

A “possible = true” preview is **advisory**, but not a strict guarantee that the transaction will in fact settle successfully, since, among other reasons:

* The user may send/receive other funds after your preview.
* The user's KYC type may change, affecting ther limits
* Their account status can change (e.g. suspended).

Example race:

1. You call `GET /transaction/transfer-preview` and receive `"possible": true`.
2. The user performs additional activity (e.g. another large transfer).
3. When you actually send the transfer, it fails or requires approval due to limits being exceeded.

> **Note:** Similar **preview / possible** endpoints exist for other flows (deposits, withdrawals). Refer to the corresponding sections and the Swagger docs for details.


# Send and Sign Transaction

For most server-side integrations, you should use:

[`POST /transaction/send-transfer`](https://api.dev.deltacrypt.net/docs#/transactions/send_transfer_transaction_send_transfer_post)

This endpoint:

1. Validates the request and checks basic constraints
2. Creates the DeltaPay transaction
3. Constructs the underlying raw blockchain transaction
4. Signs it using the private key you provide
5. Submits it to the blockchain
6. Returns a **tracking ID** you can later use to correlate callbacks and queries

<!-- TODO: be consistant with formatting -->
<!-- ### Request Parameters -->
**Request Parameters**

<!-- TODO: Update once we fixed phone_number, username, account_id thing -->
<!-- TODO: most likely to be added:
* `recipient_till_id`: *Optional[int]*
* `recipient_account_id`: *Optional[int]* (or business)
* `recipient_username`: *Optional[string]* -->
The body closely mirrors `POST /transaction/initiate-transfer`, replacing the `sender_wallet_address` with the `private_key` field.

* `private_key`: *string*
* `amount`: *number*
* `note`: *Optional[string]*
* `metadata`: *Optional[string]*
* `sender_till_id`: *Optional[int]*
* `recipient_phone_country_dialcode`: *string*
* `recipient_phone_number`: *string*
* `transaction_type`: *string* (A list of valid transaction types can be retrieved [here](https://api.dev.deltacrypt.net/transaction-types))
* `source_of_funds`: *Optional[string]*

As for similar endpoints:

The `private_key` must be [linked](../getting_started/setup.md#link-api-key) to an account.

The `metadata` is an optional free-form string (e.g., JSON-encoded string with order info).

`source_of_funds` must only be provided for transaction with `transaction_type == "cash_deposit"`.


<!-- The recipient can be identified using (`recipient_phone_country_dialcode` + `recipient_phone_number`), `recipient_username`, **or** a `recipient_business_account_id`. For personal accounts, use either the phone number or the username; for business accounts, use the business account ID. -->


<!-- ### Example Response -->
**Example Response**

```json
{
  "success": true,
  "tracking_id": "420"
}
```

The `tracking_id` corresponding to the `blockchain_transaction_id` of the transaction that was just created and can be used to poll its status, see [Get Blockchain Transaction Status](blockchain.md#get-blockchain-transaction-status).


## Manual / Raw-Transaction Flow 

If you cannot send the private key to DeltaPay, or you maintain your own signing infrastructure, you can use the more general **raw-transaction** flow documented here and in the dedicated [Blockchain Interactions](blockchain.md) section.

[`POST /transaction/initiate-transfer`](https://api.dev.deltacrypt.net/docs#/transactions/initiate_transfer_transaction_initiate_transfer_post)

**Request Parameters**

The body closely mirrors `POST /transaction/send-transfer`, replacing the `private_key` with the `sender_wallet_address` field. For a detailled explanation of the fields, refer to the [above section](#2-send-and-sign-transaction).

* `sender_wallet_address`: *string*
* `amount`: *number*
* `note`: *Optional[string]*
* `sender_till_id`: *Optional[int]*
* `recipient_username`: *Optional[string]*
* `recipient_account_id`: *Optional[int]*
* `recipient_till_id`: *Optional[int]*
* `transaction_type`: *string*
* `source_of_funds`: *Optional[string]*


**Example Response**

```json
{
  "raw_transaction": {
    "from": "0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf",
    "to": "0x52A816dB82157a5f4b2c4Fb5Be745AC4103Db674",
    "nonce": 0,
    "chainId": "1337",
    "data": "0x21d43aaf000000000.....",
    "gasLimit": "0x1ffffffffffffe",
    "gasPrice": 0,
    "type": 0
  },
  "topic": "initiate-transfer",
  "transaction_id": 166
}
```

From this point onwards, you have a `raw_transaction` object that must be

1. Signed with the private key corresponding to `sender_wallet_address`.
2. Submitted using `POST /blockchain/signed-transaction`.

Please refer to the [Blockchain Interaction](blockchain.md) section for language-specific signing examples as well as more details regarding the submission and tracking of blockchain transactions.

Here is a clean, consistent section you can append at the end.
No fluff, no ChatGPT tone — same documentation voice as the rest.


## Tracking the Transaction

Once the transfer request has been submitted (either via the recommended flow or the raw-transaction flow), the transaction must be tracked asynchronously. A successful response from `POST transaction/send-transfer` or `POST blockchain/signed-transaction` only confirms that the blockchain transaction has been accepted into the transaction pool. It does **not** guarantee that the transaction will succeed. It may still fail on-chain, or the resulting DeltaPay transaction may require approval.

Tracking can be done using either:

* (recommended) A unique value placed in the `metadata` field that you can use to correlate events on your side
* the `transaction_id` returned by the endpoint

As with C2B (Collections), there are two mechanisms for tracking status:

1. **Polling** Query the transaction status until it reaches a final state.

2. **IPNs (Callbacks)** Receive asynchronous notifications when the transaction state changes.
   The same considerations and behaviour as described in the Collections documentation apply here.

For details on polling intervals, callback handling, idempotency, and retry logic, refer to the corresponding sections in the [C2B (Collections)](c2b.md) documentation.
