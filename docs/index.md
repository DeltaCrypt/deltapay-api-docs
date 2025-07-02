# Introduction

## Abstract
This document acts as a guide for DeltaPay’s open API. It documents the features we expect will be most commonly used by our clients and partners.

We firmly believe in open and accessible APIs that anyone can access without additional charges or fees. For this reason, we have decided to make the entire REST interface used by our mobile application accessible to the public. This also means that the API is significantly more extensive than the features highlighted in this document. For a complete list of the endpoints available, please visit:

- [https://api.dev.deltacrypt.net/docs](https://api.dev.deltacrypt.net/docs)
- [https://api.prod.deltacrypt.net/docs](https://api.prod.deltacrypt.net/docs)
<!-- - [https://api.beta.deltacrypt.net/docs](https://api.beta.deltacrypt.net/docs) -->

to view the auto-generated swagger documentation online for our respective development, staging, and production environments.

## Contributing to the Documentation
The source code from which this documentation is generated is hosted on [GitHub](https://github.com/DeltaCrypt/deltapay-api-docs). Please don't hesitate to raise issues or pull requests. We are dedicated to imporoving the documentation and any feedback / input is always appreciated! 

## Environments
<!-- DeltaPay currently offers three mutually exclusive environments: development, staging, and production.

The development environment is meant for testing and incorporates any additional features or changes to the API that have not yet been published to production. It runs an identical technical setup to the production environment. Still, it does not have to abide by any regulation as the Delta on development is solely for testing and, thus, worthless.

We highly recommend testing on the development environment first before connecting to the production endpoints. If API keys are used, DeltaPay reserves the right to test the proposed applications before issuing permissions to the production API keys. -->


DeltaPay currently offers two mutually exclusive environments: development and production.

The **development** environment is designed for testing new features and changes that have not yet been published to production. It mirrors the production setup but does not need to meet regulatory requirements, as it is solely for testing purposes.

<!--The **staging** environment acts as the final testing phase before production. It closely mirrors the production environment, allowing developers to validate integrations under realistic conditions without affecting live data or transactions. We recommend using staging to perform final checks on business logic, performance, and compliance before going live.-->

The **production** environment is where real transactions take place. API keys for production access are issued after testing in development and staging environments, ensuring that integrations meet all necessary security and compliance standards.

<!-- We highly recommend testing in development first, followed by staging, before connecting to the production endpoints. -->
We highly recommend testing in development first before connecting to the production endpoints.

## API Request Guidelines
Unless otherwise specified:

- **POST** requests expect JSON-encoded data.
- **GET** and **DELETE** requests expect URL-encoded data.

All endpoints will return a status code **200 (OK)** if no exceptions occur. Other relevant response codes include:

- **404 - Not Found:** The requested resource (_e.g._, a user) does not exist.
- **401 - Unauthorized:** See [Authentication Errors](#authentication).
- **500 - Internal Server Error:** Please contact DeltaPay.

All endpoints return JSON-encoded data. If no data is returned, the response will be a generic success object:

```json
{
  "success": true
}
```

Unless otherwise specified, this is the default response format.