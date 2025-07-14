# DeltaPay QR Code JSON Specification

This document describes the JSON payload encoded in DeltaPay QR codes. Any QR code library that accepts a string input can generate a DeltaPay QR code.


## 1. Overview

* Payload is a plain JSON object.
* Null values should be omitted before encoding.
* Supports any QR library (_e.g._, `qr_flutter`, `flutter_qr_reader`, `qrcode` in JavaScript, etc.).

## 2. JSON Structure

| Field                    | Type    |  Description                            |
| ------------------------ | ------- |  -------------------------------------- |
| `username`               | String  |  Recipient's username. |
| `account_id`             | Integer | Recipient's numeric account ID. |
| `amount`                 | Number  | Transaction amount (SZL). |
| `transaction_type`       | String  | A list of valid transaction types can be retrieved [here](https://api.dev.deltacrypt.net/transaction-types).   |
| `till_id`                | Integer | Merchant's till terminal ID. |
| `note`                   | String  | Optional note that is visible to the customer. |
| `metadata`               | String  | Optional free-form metadata (can be JSON-encoded string if needed). **Not** visible to the customer.   |

<!-- | `pay_with_cashback` | Boolean | `true` to apply cashback balance; `false` or omit otherwise. | -->

**Note**: Either the `username` or `account_id` is required. If both are provided, the `account_id` takes precedence but the payment will marked as being received "through" this user. _E.g._, if the `account_id` references a business account and the user generating the QR code (and accepting the payment) is linked to the business account as an employee, he will only be able to see the incoming payment in his payment history if the transaction has been marked to be accepted by him. 

## 3. Example Payload

```json
{
  "username": "sifiso",
  "account_id": 42,
  "amount": 50.0,
  "transaction_type": "taxes",
  "till_id": 678,
  "note": "VAT",
  "metadata": "{\"tax_ref\": \"too_much\"}",
}
```
<!-- "source_of_funds": "cash", -->
<!-- "pay_with_cashback": false -->

## 4. QR Code Generation

1. Convert the JSON object to a compact string (e.g., using `json.encode`).
2. Pass the resulting string to any QR code generator.
3. Display or print the generated QR code as needed.
