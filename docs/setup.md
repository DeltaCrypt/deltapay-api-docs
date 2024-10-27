# Setup

## Client Onboarding

The client must be fully onboarded before any API integration can take place. This involves the collection and review of the client's documents as well as the account creation process. Please refer to the DeltaPay terms and conditions for more information. In particular, this process involves the following:
- DeltaPay creates the legal entity in the system
- Client submits a resolution to create the business account(s) and define the AAAs
- DeltaPay creates and sets up the account(s) as specified in the resolution

## API Key Creation

Once the client onboarding and account setup are complete, the API keys can be generated. This process can either be completed by the client himself or by DeltaPay on his behalf. The following points are worth considering:

- If the client chooses to generate the keys himself, at least one user who is registered with DeltaPay and employed or trusted by the client should be granted the following permissions:
  - `create_api_key`
  - `view_api_keys`
  - `revoke_api_key`
  
  For example, these permissions may be granted to one of the AAAs.
  
- If DeltaPay generates the API key on behalf of the client, the generated key must be shared with the client via traditional channels, such as email, which may not satisfy the client's security requirements.

If the client decides to generate the key(s) himself, he must call the following endpoint:

### `POST /legal-entity/api-key/create`

API keys are valid for five years and can be named to differentiate between them easily. They are attached to the legal entity that was specified when generating them.

The generated key is only visible once upon creation; it is the client's responsibility to store and manage it securely.

**Request Parameters**
- `legal_entity_id`: `number`
- `name`: `string`

**Required Permissions**
The caller must have the `create_api_key` permission, either generally or specifically for the targeted legal entity ID.

```json
{
  "api_key_id": 4,
  "legal_entity_id": 1,
  "prefix": "9tsIF",
  "name": "test",
  "active": true,
  "creation_time": "2024-07-17T17:01:50.837261",
  "expiration_time": "2029-07-16T17:01:50.833435",
  "api_key": "9tsIFO4XJA-viHR4ga8AW_aixe7mH7IblnB2pNjukYo"
}
```

After the API key has been created, DeltaPay will grant it permissions based on the client's requirements. Please refer to the **Permissions** chapter for more information.

### `GET /legal-entity/api-keys`

Returns the API keys attached to a legal entity.

**Request Parameters**
- `legal_entity_id`: `number`

**Required Permissions**
The caller must have the `view_api_keys` permission, either generally or specifically for the targeted legal entity.

```json
{
  "api_keys": [
    {
      "api_key_id": 1,
      "legal_entity_id": 1,
      "prefix": "OyDH-",
      "name": "test",
      "active": false,
      "creation_time": "2024-07-12T10:32:30.553105",
      "expiration_time": "2029-07-11T10:32:30.543345"
    },
    ...
    {
      "api_key_id": 4,
      "legal_entity_id": 1,
      "prefix": "9tsIF",
      "name": "test",
      "active": true,
      "creation_time": "2024-07-17T17:01:50.837261",
      "expiration_time": "2029-07-16T17:01:50.833435"
    }
  ]
}
```

Note how the API key with `id` 4 we previously created only returns the prefix and name but not the full key.

### `DELETE legal-entity/api-key/revoke`

API keys can be revoked prior to their expiry date. It is crucial to revoke keys immediately that are suspected to have been leaked. Revoked keys cannot be reactivated.

**Request Parameters**
- `api_key_id`: `number`

**Required Permissions**
The caller must have the `revoke_api_key` permission, either generally or specifically for the legal entity that the key is linked to.

## Linking API Key

As mentioned in **Blockchain Transaction Signatures**, the user must link the wallet address and account and either user or API key in order to use for it to be whitelisted on the blockchain.

Please refer to the code example for more details on this process.

In the case of API keys, this is achieved by calling the following endpoint:

### `POST /account/link-api-key`

If the API key is already linked to the account, calling this endpoint will update the wallet address. This has the same effect as unlinking and relinking with while providing a different wallet address.

**Request Parameters**
- `api_key_id`: `number`
- `account_id`: `number`
- `wallet_address`: `string`

**Required Permissions**
The caller must have the `link_api_key_to_account` permission, either generally or specifically for the account that the key is being linked to.

### `POST /account/unlink-api-key`

API keys can be unlinked again. The wallet address that was provided when linking the key will be removed from the whitelist and added to the list of deactivated wallet addresses for the account-API-key pair.

**Important**: Immediately unlink (or update) the API key if there is suspicion that the private key matching the wallet address linked to the account has been leaked. After unlinking the key, the same key can be linked again while providing a different wallet address (of a newly generated wallet). Alternatively, `POST /account/link-api-key` can be called directly with the new wallet address. This has the same effect as unlinking and relinking.

**Request Parameters**
- `api_key_id`: `number`
- `account_id`: `number`

**Required Permissions**
The caller must have the `unlink_api_key_to_account` permission, either generally or specifically for the account that the key is being unlinked from.



## Callback Registration

The user can register callbacks for a number of events that occur on the DeltaPay system. To ensure easy extensibility, the user only registers the base URL to which he wants the callback requests sent to.

For example, if the callback endpoint is `api.client.co.sz`, the IPN callback will call `POST api.client.co.sz/transaction/status`.

The following endpoints are for setting, viewing, and deactivating the callback URL for a specific account.

### `POST /account/callback-url/set`

**Request Parameters**
- `account_id`: `number`

**Required Permissions
The caller must have the `set_callback_url` permission, either generally or specifically for the account that the callback URL is set for.

### `GET /account/callback-url`

**Request Parameters**
- `account_id`: `number`

**Required Permissions**
The caller must have the `view_callback_url` permission, either generally or specifically for the account.

**Example Response**

```json
{
  "callback_url": "https://api.client.co.sz"
}
```

### `DELETE /account/callback-url/deactivate`

Sets the callback URL to null so that no more callbacks will be called for events related to this account.

**Request Parameters**
- `account_id`: `number`

**Required Permissions**
The caller must have the `set_callback_url` permission, either generally or specifically for the account for which the callback URL is being deactivated.

