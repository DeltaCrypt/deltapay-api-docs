# Permissions

The permissions for accessing non-blockchain functions are organized as follows:

- **General Permissions:** These apply broadly across the system.
- **Targeted Permissions:** These apply to specific targets, in particular:
  - User
  - Account
  - Legal Entity

> **Note:** No permissions are needed when a `UserTargetPermission` is required and the caller is the target user. This allows users to request their own data without requiring specific permissions. Any exceptions to this rule will be clearly stated.

## Roles

General permissions can be attached to a role, which may then be assigned to a user or API key. This allows for logical grouping of permissions and avoids having to assign them individually.

> **Note:** Permissions assigned to a role are always general (they do not apply to a specific target).

## User and API Key Permissions

There are two types of callers:

- **Users:** Who will typically authenticate using an OAuth token.
- **Servers:** Which will typically authenticate using an API key.

Both users and API keys can have permissions assigned to them and provide a cognate set of endpoints to grant, view, and revoke roles and permissions respectively. For users there is:

- `POST /user/grant-role`
- `POST /user/grant-account-permissions`
- `POST /user/grant-user-permissions`
- `POST /user/grant-legal-entity-permissions`
- `GET /user/roles`
- `GET /user/permissions`
- `DELETE /user/revoke-role`
- `DELETE /user/revoke-account-permissions`
- `DELETE /user/revoke-user-permissions`
- `DELETE /user/revoke-legal-entity-permissions`

For API keys there is:

- `POST /api-key/grant-role`
- `POST /api-key/grant-account-permissions`
- `POST /api-key/grant-user-permissions`
- `POST /api-key/grant-legal-entity-permissions`
- `GET /api-key/roles`
- `GET /api-key/permissions`
- `DELETE /api-key/revoke-role`
- `DELETE /api-key/revoke-account-permissions`
- `DELETE /api-key/revoke-user-permissions`
- `DELETE /api-key/revoke-legal-entity-permissions`

For more detailed documentation on the endpoints above, please refer to the online documentation. For demonstration purposes, we will highlight the following:

### `POST /user/grant-account-permissions`

Multiple permissions can be granted for the same user and target account. This is common because, for instance, an account admin gains many permissions simultaneously when assigned the admin role. Different account targets will require separate calls.

> **Note:** Granting a permission twice will not throw an error, but simply be ignored.

**Request Parameters**
- `subject_user_id`: `number`
- `permissions`: `Array[string]`
- `target_account_id`: `number`

**Required Permissions**
The caller must have the general `grant_account_permission` permission.

### `GET /user/permissions`

**Request Parameters**
- `user_id`: `Optional[number]`

If the `user_id` is not provided and the caller uses an OAuth token to authenticate the call, it can be determined from the token.

**Required Permissions**
The caller must have the `view_permissions` permission, either generally or specifically for the user. As described at the beginning of the Permissions chapter, users do not need any permissions to view their own data.

**Example Response**
```json
{
    {
      "permission": "view_spending_allowance",
      "target_type": "general"
    },
    ...
    {
      "permission": "view_transactions",
      "target_type": "general"
    },
    {
      "permission": "view_account_info",
      "target_type": "account_list",
      "target_account_ids": [
        1001,
        1004,
        1006
      ]
    },
    ...
```

### `DELETE /user/revoke-account-permissions`

This endpoint can be used to revoke either a specific or all permission(s) for a certain user or target account.

**Request Parameters**
- `subject_user_id`: `number`
- `target_account_id`: `number`
- `permissions`: `Optional[string]`

If permission is null, all permissions are revoked for the target account.

**Required Permissions**
The caller must have the general `revoke_account_permission` permission.
