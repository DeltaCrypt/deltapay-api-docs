# C2B

The process of receiving money from a customer encompasses the following:

1. Receive a callback when the transaction status changes (IPN).
2. View the transaction.

We are working on a feature that will allow for prompting the customer to initiate via a notification sent to their device that, when clicked, will pre-fill the send money dialog. Until then, the user must enter the information manually.

## IPN

To receive IPNs, the user must first register the base callback URL as described in the Setup section. The callback is triggered for both the **sender and recipient accounts** using the registered callbacks for the respective accounts, if available. The callback URL format is as follows:

    base URL + /transaction/status


The notification payload includes the `transaction_id` and `status`. Based on the transaction status, the client can determine whether to retrieve more detailed information about the transaction.

**Important:** This callback is not signed, meaning it could originate from anyone. The user must call `GET /full-transaction/from-id` to confirm the transaction data.

**Example Callback Body**
```json
{
    "transaction_id": 42,
    "status": "succeeded"
}
```

The following transaction statuses are notified about:

- initiated
- approved
- succeeded
- failed

> **Note:** Transactions that do not require approval or finalization will automatically move to the approved or succeeded state. For instance, a bank deposit initiated by a user with sufficient spending allowance will begin in the approved state. Similarly, a transfer that does not require approval will immediately be marked as succeeded.

## Querying Transactions

### `GET /full-transaction/from-id`

This endpoint returns all the details on the transaction as opposed to `GET accounts/transactions`, which returns transactions from the calling account's perspective.

The caller can optionally specify the account from whose perspective the amount, fee, and commission will be viewed. To demonstrate this, consider a cash withdrawal of E10. The sender (_i.e._, the user withdrawing the cash) pays a fee calculated as:

    fee(x) = 1 + 0.015x

and 1% goes as commission to the recipient (_i.e._, the merchant offering the withdrawal). This will result in the following responses from the endpoint, depending on which account is specified in the `caller_account_id`:

- `caller_account_id = sender_account_id`
    ```json
    {
        "transaction_id": 42,
        ...
        "amount": 10,
        "cashback_received": 0,
        "cashback_spent": 0,
        "fee": 1.15,
        "commission_amount": 0,
        ...
    }
    ```

- `caller_account_id = recipient_account_id`
    ```json
    {
        "transaction_id": 42,
        ...
        "amount": 10,
        "cashback_received": 0,
        "cashback_spent": 0,
        "fee": -0.1,
        "commission_amount": 0.1,
        ...
    }
    ```

- `caller_account_id = null`
    ```json
    {
        "transaction_id": 42,
        ...
        "amount": 10,
        "cashback_received": 0,
        "cashback_spent": 0,
        "fee": 1.05,
        "commission_amount": 0.1,
        ...
    }
    ```

**Request Parameters**

- `transaction_id`: `number`
- `caller_account_id`: `Optional[number]`

**Required Permissions**

The caller must have the `view_transactions` permission, either generally or specifically for the sender or recipient account. Furthermore, the user's permissions and their potential attachment as an employee to the accounts involved in the transaction will determine whether they can see details on the initiator, approver, and finalizer.


**Example Response**
```json
{
  "transaction_id": 42,
  "transaction_type": "cash_withdrawal",
  "transaction_status": "succeeded",
  "initialisation_time": "2024-07-15T19:11:07.247411",
  "settled_time": "2024-07-15T19:11:11.890845",
  "note": "hello world + metadata",
  "source_of_funds": "",
  "bank_account": null,
  "sender_account_id": 123,
  "sender_account_name": "Personal",
  "sender_name": "adrian",
  "sender_till_name": null,
  "recipient_account_id": 60,
  "recipient_account_name": "Mbabane Office",
  "recipient_name": "DeltaPay",
  "recipient_till_name": "Desk 1",
  "amount": 10,
  "cashback_received": 0,
  "cashback_spent": 0,
  "fee": 1.05,
  "commission_amount": 0.1,
  "initiator": {
    "username": "adrian",
    "legal_name": "Adrian Albert Koch"
  },
  "approver": null,
  "finaliser": null
}
```
