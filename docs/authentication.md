# Authentication

DeltaPay's API supports three authentication methods:
1. OAuth 2.0 token
2. API Key
3. Blockchain transaction signatures

## OAuth 2.0 Token
Used for individual user authentication. The `access_token` should be included as a Bearer token in requests.

### Example Login Response
```json
{
  "token_type": "bearer",
  "access_token": "eyJraWQiOiI...",
  "refresh_token": "eyJjdHkiOi...",
  "user_id": 1,
  "username": "adrian"
}
