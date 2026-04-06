# DeltaPay Bulk Payment Import CSV Specification

## 1. Purpose

This CSV format is used to submit bulk payment instructions into DeltaPay.

It supports the following payment routes:

* **DELTA**: DeltaPay to DeltaPay payments
* **EPS**: EPS fast payments (below **E50,000**)
* **BANK**: bank transfer payments, typically for payments above **E50,000**

Each CSV row represents exactly one payment instruction.


## 2. File format

* File type: **CSV**
* Encoding: **UTF-8**
* Delimiter: **comma (, )**
* First row: **header row required**
* One payment instruction per row
* Empty values should be left blank
* Do not include formulas or multiple values in one cell

### General rules

* Column names must match the specification exactly
* Amounts must use a decimal point, for example `1500.00` (Maximum of two decimal points)
* No currency column is included; all amounts are assumed to be **SZL / E**
* Values are **case-sensitive** and must match exactly
* No abbreviations or alternative spellings are allowed
* Any value outside this list will result in validation failure

### Phone number format

All phone numbers in the CSV must

* be in **international format without the "+" symbol**
* contain **country code + number**
* contain **digits only (no spaces, dashes, or brackets)**

**Example**

```
26878725616
```

### Validation behaviour

#### File-level validation

- Invalid CSV format → entire file rejected
- Missing required headers → entire file rejected

#### Row-level validation

- Invalid rows are rejected individually
- Valid rows are still processed (partial success allowed)
- Only fields relevant to the selected `payment_method` may be populated
- Any unrelated field being non-empty must result in validation failure

### Whitespace

- No leading or trailing whitespace allowed
- Empty strings and whitespace-only values are treated as empty


## 3. High-level design

The file uses one required routing field:

* `payment_method`

Allowed values:

* `DELTA`
* `EPS`
* `BANK`

This determines which recipient fields are required for that row.

## 4. Column specification

### 4.1 Common columns

These columns apply to all rows.

| Column             |                    Required | Type    | Description                                                                   |
| ------------------ | --------------------------: | ------- | ----------------------------------------------------------------------------- |
| `payment_method`   |                         Yes | enum    | One of `DELTA`, `EPS`, `BANK`                                                 |
| `amount`           |                         Yes | decimal | Payment amount in SZL                                                         |
| `note`             |                          No | string  | Human-readable payment note                                                   |string, max 512 characters      |
| `client_reference` | No but strongly recommended | string  | Free-form external reference or JSON system for reconciliation and idempotency |

>**Note: ** The `client_reference` should be globally **unique** accross all transactions past, current, and future (*e.g.* 64 character uuid)

#### Amount validation

- Must be greater than `0`
- Maximum of 2 decimal places
- Must not exceed system or regulatory limits
    - For `EPS`, must be `<= 50,000`
    - For `BANK`, must be `> 50,000` (if you want strict routing separation)


### 4.2 DELTA recipient columns

These columns are used only when `payment_method = DELTA`.

Exactly **one** of the following must be provided:

* `delta_recipient_account_id`
* `delta_recipient_username`
* `delta_recipient_phone_number`

| Column                         | Required for DELTA | Type   | Description           |
| ------------------------------ | -----------------: | ------ | --------------------- |
| `delta_recipient_account_id`   |      Conditionally | string | DeltaPay account ID   |
| `delta_recipient_username`     |      Conditionally | string | DeltaPay username     |
| `delta_recipient_phone_number` |      Conditionally | string | DeltaPay phone number |
| `transaction_type` |          No but recommended | string  | Source-defined transaction type, preferably populated for DeltaPay processing |


The `transaction_type` field is optional but **strongly recommended** for DELTA payments.
The following values are allowed for bulk upload:
* `income`
* `groceries`
* `transportation`
* `rent`
* `utilities`
* `healthcare`
* `education`
* `airtime`
* `clothing`
* `household`
* `entertainment`
* `business`
* `taxes`
* `savings`
* `eating_out`
* `deceased`
* `other`

If not provided, it will deafult to `income`.


### 4.3 EPS recipient columns

These columns are used only when `payment_method = EPS`.

Exactly **one** of the following must be provided:
  * `eps_recipient_account_number`
  * `eps_recipient_phone_number`

| Column                         | Required for EPS | Type   | Description                                     |
| ------------------------------ | ---------------: | ------ | ----------------------------------------------- |
| `eps_recipient_agent_id`       |              Yes | string | EPS agent / institution identifier              |
| `eps_recipient_account_number` |    Conditionally | string | Recipient bank account or wallet account number |
| `eps_recipient_phone_number`   |    Conditionally | string | Recipient mobile number                         |

**For EPS rows:**


>**Note:** The amount must be **less than or equal to E50,000**, subject to DeltaPay and EPS validation rules


The `eps_recipient_agent_id` must be a valid **National Payment Switch participant identifier** as defined by the Central Bank of Eswatini.

According to the *National Payment Switch Participant Identification document (v1.5)* , the following identifiers are supported:

### Banks

* `103001` — Eswatini Bank
* `103002` — First National Bank
* `103003` — Nedbank
* `103004` — Standard Bank
* `103005` — Swaziland Building Society
* `103006` — Central Bank of Eswatini

### Mobile Wallet Providers

* `203001` — Eswatini Mobile
* `203002` — InstaCash
* `203003` — MTN
* `203004` — Standard Bank (Unayo)
* `203005` — Swaziland Building Society
* `203006` — DeltaPay

### 4.4 BANK recipient columns

These columns are used only when `payment_method = BANK`.

| Column                          | Required for BANK | Type   | Description                                                     |
| ------------------------------- | ----------------: | ------ | --------------------------------------------------------------- |
| `bank_recipient_account_holder` |               Yes | string | Name of the bank account holder                                 |
| `bank_recipient_account_number` |               Yes | string | Bank account number                                             |
| `bank_recipient_bank_code`      |               Yes | string | Bank identifier from a DeltaPay-supported enum / reference list |
| `bank_recipient_branch_code`    |               Yes | string | Branch code                                                     |

The `bank_recipient_bank_code` field must use one of the following exact values:

* `FNB_SZ` — First National Bank
* `STB_SZ` — Standard Bank
* `NED_SZ` — Nedbank
* `ESW_SZ` — Eswatini Bank

## 5. Header definition

The recommended full CSV header is:

```csv
payment_method,amount,note,client_reference,transaction_type,delta_recipient_account_id,delta_recipient_username,delta_recipient_phone_number,eps_recipient_agent_id,eps_recipient_account_number,eps_recipient_phone_number,bank_recipient_account_holder,bank_recipient_account_number,bank_recipient_bank_code,bank_recipient_branch_code
```

### 5.1 DELTA row

Must populate:

* `payment_method = DELTA`
* `amount`
* exactly one DELTA recipient field

Must leave blank:

* all EPS fields
* all BANK fields

### 5.2 EPS row

Must populate:

* `payment_method = EPS`
* `amount`
* `eps_recipient_agent_id`
* exactly one of `eps_recipient_account_number` or `eps_recipient_phone_number`

Must leave blank:

* all DELTA fields
* all BANK fields

### 5.3 BANK row

Must populate:

* `payment_method = BANK`
* `amount`
* all BANK recipient fields

Must leave blank:

* all DELTA fields
* all EPS fields
