# Payment Request API

The Payment Request API allows for the creation and management of requests for payments.

The recipient of the payment request (PR) receives a push notification and the PR is displayed on their home screen until either accepted or rejected. 

PRs can only be sent to individual users. When accepting the PR, the user can chose the account from which to pay.


## Creating a payment request

[`POST /payment-request/create`](https://api.dev.deltacrypt.net/docs#/payment_request/create_payment_request_payment_request_create_post)

**Description:**
Requesting a payment from a user. The user is specified either by their username or the phone number they used to sign up with DeltaPay.

**Request Parameters**

- `account_id`: *int*
- `amount`: *number*
- `transaction_type`: *string*  (A list of valid transaction types can be retrieved [here](https://api.dev.deltacrypt.net/transaction-types))
- `till_id`: *Optional[int]*
- `note`: *Optional[string]*
- `metadata`: *Optional[string]*
- `phone_country_dialcode`: *Optional[string]* (do not inlcude a '+')
- `phone_number`: *Optional[string]*
- `username`: *Optional[string]*

The `account_id` specifies the the recipient account that the payment is being requested into.

Either `username` **or** both `phone_country_dialcode` and `phone_number` must be provided.

The `metadata` is an optional free-form string (e.g., JSON-encoded string with order info).

**Required Permissions**

The caller must have the `create_payment_request` permission, either generally or specifically for the account.

<!-- Add docs on the till id  -->


## Viewing Incoming Payment Requests

[`GET /user/payment-requests/incoming`](https://api.dev.deltacrypt.net/docs#/payment_request/get_incoming_payment_requests_from_user_id_user_payment_requests_incoming_get)

This endpoint returns a list of PRs that have been sent to the specified user.
The sender of the PR is returned as a

 - user, if the account is a personal account
 - legal entity, if the account is a business account

**Request Parameters**

- `user_id`: *int*
- `status`: *string*

**Required Permissions**

The caller must have the `view_payment_requests` permission, either generally or specifically for the user.


## Viewing Outgoing Payment Requests

There are two endpoints for getting RPs outgoing from a user and a legal entity, respectively.


[`GET /user/payment-requests/outgoing`](https://api.dev.deltacrypt.net/docs#/payment_request/get_outgoing_payment_requests_from_user_id_user_payment_requests_outgoing_get)

This endpoint returns all PRs that request funds to be sent to an account the user is linked to.

**Request Parameters**

- `user_id`: *int*
- `status`: *string*

**Required Permissions**

The caller must have the `view_payment_requests` permission, either generally or specifically for the user.


[`GET /legal-entity/payment-requests/outgoing`](https://api.dev.deltacrypt.net/docs#/payment_request/get_outgoing_payment_requests_from_legal_entity_id_legal_entity_payment_requests_outgoing_get)

This endpoint returns all PRs that request funds to be sent to an account the legal entity is linked to.

**Request Parameters**

- `legal_entity_id`: *int*
- `status`: *string*

**Required Permissions**

The caller must have the `view_payment_requests` permission, either generally or specifically for the legal entity. 



## Payment Request state

A PR can be in one of the following states:

- pending
- cancelled
- rejected
- approved
- succeeded
- failed

When a PR is created, it will be in the pending state, from there on the following actions trigger the respective state changes:

| Action                | State Change                  |
| --------------------- | ----------------------------- |
| sender cancels        | pending &rarr; cancelled      |
| recipinet rejects     | pending &rarr; rejected       |
| recipient approves    | pending &rarr; approved       |
| transaction succeeds  | approved &rarr; succeeded     |
| transaction fails     | approved &rarr; failed        |

<!-- Can we always go suceeded / failed?? -->

No other state changes are possible; *e.g.* pending &rarr; succeeded can never occur, as it 