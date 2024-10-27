# Introduction

## Abstract
This document acts as a guide for DeltaPay’s open API. It documents the features we expect will be most commonly used by our clients and partners.

We firmly believe in open and accessible APIs that anyone can access without additional charges or fees. For this reason, we have decided to make the entire REST interface used by our mobile application accessible to the public. This also means that the API is significantly more extensive than the features highlighted in this document. For a complete list of the endpoints available, please visit:

- [https://api.dev.deltacrypt.net/docs](https://api.dev.deltacrypt.net/docs)
- [https://api.beta.deltacrypt.net/docs](https://api.beta.deltacrypt.net/docs)

to view the auto-generated documentation online for our respective development and production environments.

## Environments
DeltaPay currently offers two mutually exclusive environments: development and production.

The development environment is meant for testing and incorporates any additional features or changes to the API that have not yet been published to production. It runs an identical technical setup to the production environment. Still, it does not have to abide by any regulation as the Delta on development is solely for testing and, thus, worthless.

We highly recommend testing on the development environment first before connecting to the production endpoints. If API keys are used, DeltaPay reserves the right to test the proposed applications before issuing permissions to the production API keys.

## API Request Guidelines
Unless otherwise specified:

- **POST** requests expect JSON-encoded data.
- **GET** and **DELETE** requests expect URL-encoded data.

All endpoints will return a status code 200 (OK) if no exceptions occur. Other relevant response codes include:

- **404 - Not Found:** The requested resource (e.g., a user) does not exist.
- **401 - Unauthorized:** See [Authentication Errors](#authentication-errors).
- **500 - Internal Server Error:** Please contact DeltaPay.

All endpoints return JSON-encoded data. If no data is returned, the response will be a generic success object:

```json
{
  "success": true
}
```

Unless otherwise specified, this is the default response format.