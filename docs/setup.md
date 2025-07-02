# Client Onboarding

The client must be fully onboarded before any API integration can take place. This involves the collection and review of the client's documents as well as the account creation process. Please refer to the DeltaPay terms and conditions for more information. In particular, this process involves the following:
- DeltaPay creates the legal entity in the system
- Client submits a resolution to create the business account(s) and define the AAAs
- DeltaPay creates and sets up the account(s) as specified in the resolution

# API Key Creation

Once the client onboarding and account setup are complete, the API keys can be generated. This process can either be completed by the client himself or by DeltaPay on his behalf. The following points are worth considering:

- If the client chooses to generate the keys himself, at least one user who is registered with DeltaPay and employed or trusted by the client should be granted the following permissions:
  - `create_api_key`
  - `view_api_keys`
  - `revoke_api_key`
  
  For example, these permissions may be granted to one of the AAAs.
  
- If DeltaPay generates the API key on behalf of the client, the generated key must be shared with the client via traditional channels, such as email, which may not satisfy the client's security requirements.

If the client decides to generate the key(s) himself, he must call the following endpoint:

## Create API Key
[`POST /legal-entity/api-key/create`](https://api.dev.deltacrypt.net/docs#/legal_entities/create_api_key_legal_entity_api_key_create_post)

API keys are valid for five years and can be named to differentiate between them easily. They are attached to the legal entity that was specified when generating them.

The generated key is only visible once upon creation; it is the client's responsibility to store and manage it securely.

**Request Parameters**
- `legal_entity_id`: *int*
- `name`: *string*

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

## Get API Keys
[`GET /legal-entity/api-keys`](https://api.dev.deltacrypt.net/docs#/legal_entities/get_api_keys_from_legal_entity_id_legal_entity_api_keys_get)

Returns the API keys attached to a legal entity.

**Request Parameters**
- `legal_entity_id`: *int*

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

## Revoke API Key
[`DELETE legal-entity/api-key/revoke`](https://api.dev.deltacrypt.net/docs#/legal_entities/deactivate_api_key_legal_entity_api_key_revoke_delete)

API keys can be revoked prior to their expiry date. It is crucial to revoke keys immediately that are suspected to have been leaked. Revoked keys cannot be reactivated.

**Request Parameters**
- `api_key_id`: *int*

**Required Permissions**
The caller must have the `revoke_api_key` permission, either generally or specifically for the legal entity that the key is linked to.

## Linking API Key

As mentioned in **Blockchain Transaction Signatures**, the user must link the wallet address and account and either user or API key in order to use for it to be whitelisted on the blockchain.

Please refer to the code example for more details on this process.

In the case of API keys, this is achieved by calling the following endpoint:

## Link API Key
[`POST /account/link-api-key`](https://api.dev.deltacrypt.net/docs#/accounts/register_wallet_address_to_api_key_account_link_api_key_post)

If the API key is already linked to the account, calling this endpoint will update the wallet address. This has the same effect as unlinking and relinking with while providing a different wallet address.

**Request Parameters**
- `api_key_id`: *int*
- `account_id`: *int*
- `wallet_address`: *string*

**Required Permissions**
The caller must have the `link_api_key_to_account` permission, either generally or specifically for the account that the key is being linked to.

### `POST /account/unlink-api-key`

API keys can be unlinked again. The wallet address that was provided when linking the key will be removed from the whitelist and added to the list of deactivated wallet addresses for the account-API-key pair.

**Important**: Immediately unlink (or update) the API key if there is suspicion that the private key matching the wallet address linked to the account has been leaked. After unlinking the key, the same key can be linked again while providing a different wallet address (of a newly generated wallet). Alternatively, `POST /account/link-api-key` can be called directly with the new wallet address. This has the same effect as unlinking and relinking.

**Request Parameters**
- `api_key_id`: *int*
- `account_id`: *int*

**Required Permissions**
The caller must have the `unlink_api_key_to_account` permission, either generally or specifically for the account that the key is being unlinked from.



## Callback Registration

The user can register callbacks for a number of events that occur on the DeltaPay system. To ensure easy extensibility, the user only registers the base URL to which he wants the callback requests sent to.

For example, if the callback endpoint is `api.client.co.sz`, the IPN callback will call `POST api.client.co.sz/transaction/ipn`.

The following endpoints are for setting, viewing, and deactivating the callback URL for a specific account.

### Register callback
[`POST /account/callback-url/register`](https://api.dev.deltacrypt.net/docs#/accounts/register_callback_url_account_callback_url_register_post)

1. Registers the callback for the account.
2. Generates a new signing key pair. The public key is returned required to verify the signatures.

<!-- Explain what the purpose of the manager legal entity is -->

**Request Parameters**
- `callback_url`: *string*
- `account_id`: *int*
- `manager_entity_id`: *int* - The legal entity that is in charge of managing this callback
<!-- Check if optional -->

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
- `account_id`: *int*
- `manager_entity_id`: *Optional[int]*

**Required Permissions**
The caller must have the `view_callback_url` permission, either generally or specifically for the account **and** manager legal entity.

**Example Response**

```json
{
    "callback_urls": [
        {
            "callback_id": 4,
            "callback_url": "https://api.dev.deltacrypt.net",
            "account_id": 1004,
            "manager_entity_id": 1,
            "signing_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA57xXfRBtvwwotZBjW+zW\n7GzPchUlgzqJL5epFKL15E0gqgIu7O1fvnohpBdHe2uEAlGhJWw/LUsAKrYQECau\nm6gBEC6TWMzG8ne8yU5QH2lLq4J4BL4slHTSN//t7vejZu02N33STZP5CoS0bJ5f\nImk4s69jp5vjesUussFqBmVUHbEYn3D+Ihz/Hbrwx61EC0hRwBcTTYHCXgDEey3P\n0dztvs+WKP00qiUg8Eb16kaooA1/fI3ZaW94QnYYfH9UKspiJWtUfapdNExv1utD\ndOHZhdkbbtX8/JG3LZIyjUGrnxfDu0wC5RKWltBzKjzHn/b0Ai7xrElWfgjmRPtZ\nwQIDAQAB\n-----END PUBLIC KEY-----\n",
            "active": true,
            "deactivation_time": null
        },
        {
            "callback_id": 1,
            "callback_url": "test",
            "account_id": 1004,
            "manager_entity_id": 1,
            "signing_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvDRW7vlW0w2uEwpZe5F0\nNtDsWFtf28GWFbRgkEjx2LHV2KmkuzuJgtATcfVoSZPZBTwVfRGfhh6k4j8Fn8iY\nLUhac+rSoUvEpdyq35l/K9rwp84n8DIk9GBA55ragqiu+opA94Jn9MA2koRhyO0H\n/wn6fvZME0hpR63emBq0t+Q7X3mjiISZZwHP60YX98SfYGMOpD2yhdTp08DX28pC\nMNH4kdBbbXCKu1UGHn2MZmTJykeFFf69aJx4QF7QnQDgZ+wXIZ4as6jH8YmKrEKe\n2nTP0JONxWJjgqon7nyKFSaSMovbdfwkIwMxEHozKLfaqbxHPkq/Djc8BTuD6k2l\nOwIDAQAB\n-----END PUBLIC KEY-----\n",
            "active": false,
            "deactivation_time": "2024-10-26T14:54:21.178337"
        }
    ]
}
```

### Deactivate callback
[`DELETE /account/callback-url/deactivate`](https://api.dev.deltacrypt.net/docs#/accounts/deactivate_callback_url_account_callback_url_deactivate_delete)

<!-- Sets the callback URL to null so that no more callbacks will be called for events related to this account. -->

**Request Parameters**
- `callback_id`: *int*

**Required Permissions**
The caller must have the `set_callback_url` permission, either generally or specifically for the account **and** manager legal entity. 

