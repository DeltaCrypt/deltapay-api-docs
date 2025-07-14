# Authentication

The API uses three ways of authentication:
- OAuth 2.0 token
- API Key
- Blockchain transaction signatures

The OAuth 2.0 token and API Key can largely be used interchangeably, whereas functions that entail state changes on the blockchain will generally have to be signed locally by the client.

> **Note**: For the endpoints that allow authentication using both the token and API key, **either or the other** must be passed.


## OAuth 2.0 Token

This form of authentication is designed for individual users. The generated token contains the `user_id` and can be used to determine the caller without the need to explicitly provide the `user_id`.


### Login Endpoint
The `POST /login` endpoint expects `x-www-form-url-encoded` data. This is an exception, as all other POST endpoints expect JSON-encoded data.

**Request Parameters**

- `username`: `string`
- `password`: `string`

**Example Response**
```json
{
  "token_type": "bearer",
  "access_token": "eyJraWQiOiI.......",
  "refresh_token": "eyJjdHkiOiJK......",
  "user_id": 1,
  "username": "adrian",
  "phone_country_dialcode": "268",
  "phone_number": "24045443",
  "first_name": "Adrian Albert",
  "last_name": "Koch"
}
```

The login endpoint returns two distinct tokens:

- `access_token`: Used to authenticate requests. Generally valid for 15 minutes unless revoked.
- `refresh_token`: Used to obtain a new access token by calling the `POST /refresh-access-token` endpoint.


### Usage Example
The `access_token` must be passed as a bearer token in the API request header. Below is an example call to the `GET /user` endpoint:

    curl -X 'GET'
      'https://api.dev.deltacrypt.net/user'
      -H 'accept: application/json'
      -H 'Authorization: Bearer eyJraWQi......'

> **Note**: The `user_id` does not need to be explicitly passed, as it can be determined from the token. If a value is provided, it will have precedence.


## API Key

Authentication using an API token is designed for institutions that want to connect to the API in a programmatic manner. See the **API Key Creation** section for more detail on how to create and link API tokens.

Multiple tokens can be linked to the same legal entity with varying sets of permissions attached to them.

The API key must be passed as `x-api-key` in the API request header. Below is an example call to the `GET /user` endpoint:

    curl -X 'GET' \
      'https://api.dev.deltacrypt.net/user?user_id=2' \
      -H 'accept: application/json' \
      -H 'x-api-key: KGD7Wf.....'

> **Note**: In contrast to the `access_token` usage, the `user_id` must be provided in the request as it cannot be determined from the API key.


## Authentication Errors

Errors that occur in connection with authentication result in the response code **401 (Unauthorized)**.

The error response will provide details on the type of exception, _e.g._

```json
{
  "detail": "Token expired"
}
```

The following exceptions can occur:

- Not authorized
- Username or password incorrect
- User not confirmed
- Username not found
- Could not validate credentials
- Failed to validate token
- Invalid API key
- API key has expired
- API key has been revoked
- Provide either a token or an API key, not both
- Either a token or an API key must be provided

**SignUp**:

- Failed
- User not found
- Username not found
- User already registered
- Username already in use
- Password does not meet the requirements
- Confirmation code is incorrect
- Confirmation code has expired
- Attempt limit exceeded

**Login**:

- Failed
- Another challenge is required
- Username not found in the database

**Refresh Access Token**: Failed

**Forgot Password**:

- Failed
- Username not found
- Attempt limit exceeded
- Confirmation code is incorrect
- Confirmation code has expired
- Too many failed attempts
- Password does not meet the requirements

**Change Password**:

- Failed
- Password does not meet the requirements
- Attempt limit exceeded

**Change Phone Number**:

- Failed
- Code is incorrect
- Code has expired
- Attempt limit exceeded

Another common cause for an endpoint to return 401 (Unauthorized) is missing permissions, _e.g._

```json
{
  "detail": "API key does not have the required permission: view_kyc_data (target_user_id: 2)"
}
```


## Blockchain Transaction Signatures

The interaction with the blockchain follows three simple steps:

1. Obtain the raw blockchain transaction (generally using one of the GET endpoints prefixed with raw).
2. Sign the transaction locally using the Ethereum wallet previously generated.
3. Optionally query the state of the blockchain transaction.

For more details on specific endpoints, please refer to the example attached to this document or contact DeltaPay directly.

For the transaction to succeed, the wallet used to sign it must be whitelisted on the blockchain. This requires the caller to provide the public wallet address of the wallet they want to link to the API-key-account (or user-account) pair, which happens implicitly in one of the following ways:

- `POST /account/link-api-key`
- `POST /account/create-personal`
- `POST /account/register-business`

For the purpose of this document, we focus on the scenario where API keys are used. For more details on linking an API key to an account, refer to **Linking API Key** in the setup section.

<!-- TODO: Fix this note (or reformat) -->
> **Note**: Transactions signed by a wallet linked to an API key differ in some ways from those linked to a user. In particular:

> - API Keys do not have a spending allowance. Therefore, no transaction initiated by an API key will ever need to be approved.
> - API keys cannot approve other transactions.
> - API keys cannot set spending allowances.
> - API keys cannot deactivate accounts.

Should you require any of the above features, please contact DeltaPay directly.
