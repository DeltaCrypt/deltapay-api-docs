
# Eswatini Payment Switch (EPS)

The **EPS (Eswatini Payment Switch)** is the national payment infrastructure operated under the oversight of the Central Bank of Eswatini. It connects banks, mobile money providers, and other financial institutions into a single interoperable network.

### Why it matters

- **Interoperability:** Enables transfers across different institutions (banks, mobile wallets, and fintechs) instead of siloed systems.  
- **Real-time payments:** Supports near-instant transactions between participants.  
- **Standardisation:** Provides a common scheme, message formats, and rules for all integrations.  
- **Financial inclusion:** Expands reach by allowing users on different platforms to transact seamlessly.  
- **Regulatory backbone:** Acts as the core infrastructure for national payment flows under central bank governance.


### Access via DeltaPay APIs

The EPS is accessible directly through the existing DeltaPay APIs, meaning no separate integration, licensing, or onboarding onto the switch is required.

By integrating once with DeltaPay, you gain **all-in-one access** to the national payment network, allowing you to use your DeltaPay account to **collect from and disburse to any domestic institution** (banks, mobile money providers, and other participants).

DeltaPay abstracts the complexity of the switch, handling connectivity, settlement, and collateral requirements, so you can focus purely on your product and user experience.

<!-- # EPS Overview -->

## EWLT vs ACCT:

EPS distinguishes between two account schemes. **EWLT** (eWallet) refers to mobile money accounts, typically identified by phone-number-based formats. **ACCT** (Account) refers to traditional bank accounts, which follow institution-specific account numbering structures.  

**Exception – DeltaPay:**  
While DeltaPay supports both account-based and wallet-based user models internally, all DeltaPay accounts are represented as **EWLT** on the switch.

## Current EPS Participants

The following section is based on the Wallet and Account Guidelines published by the Central Bank of Eswatini.

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

On the DeltaPay side, the transaction is processed like any other incoming transaction. Subscribers will receive updates via the standard [IPNs](../common_usecases/c2b.md#instant-payment-notification-ipn) (Instant Payment Notifications), with status changes for any transactions linked to the registered account ID.

The **payment reference** provided by the sender is mapped to the `note` field in DeltaPay.

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

## DeltaPay-Specific Behaviour (Incoming Payments)

For incoming EPS transactions into DeltaPay:
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

Therefore, incoming EPS transactions can be handled using the same logic as standard DeltaPay-to-DeltaPay transactions, as funds are effectively credited (“minted”) into the recipient account.


## Payment References

The EPS currently does not support a native Request to Pay mechanism or structured metadata fields comparable to DeltaPay payment requests.

As a result:

- There is no guaranteed way to attach structured metadata that will be returned with the transaction.
- Senders may optionally include a payment reference on their originating platform.

This reference is received in DeltaPay as the note field and can be used for reconciliation by matching payments beyond sender, amount, and timestamp.

For reconciliation and business logic, integrators should rely on:

- `transaction_status`
- `eps_debtor_account_id` (sender)
- `amount`
- `timestamp`
- `note` (payment reference, if provided)


## Example Payload (Incoming) # TODO

## Example Payload (Outgoing)

```json
{
    "transaction_id": 10000,
    "transaction_type": "eps_withdrawal",
    "transaction_status": "approved",
    "initialisation_time": "2026-04-22T18:00:50.148951",
    "settled_time": null,
    "note": "Initiated EPS Withdrawal",
    "metadata": null,
    "source_of_funds": null,
    "bank_account": null,
    "sender_account_id": 14,
    "sender_account_name": "Main",
    "sender_name": "MinenhleGrocery",
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
    "eps_debtor_account_id": "14",
    "eps_debtor_name": null,
    "eps_debtor_account_scheme": "EWLT",
    "eps_instructing_agent_id": "203006",
    "eps_instructing_agent_name": "DeltaPay",
    "eps_creditor_account_id": "12345678",
    "eps_creditor_name": null,
    "eps_creditor_account_scheme": "ACCT",
    "eps_instructed_agent_id": "203002",
    "eps_instructed_agent_name": "Instacash",
    "promotion_data": null,
    "signature": "E4hLq13GRblPnJ............."
}
```