# Introduction

## Abstract
This document provides a guide for DeltaPay’s open API, highlighting commonly used features. The API is open to public access and offers extensive endpoints. Visit the full documentation online:
- [Development Environment](https://api.dev.deltacrypt.net/docs)
- [Production Environment](https://api.beta.deltacrypt.net/docs)

## Environments
DeltaPay has two environments: **development** and **production**. It is recommended to test integrations in the development environment first.

## API Request Guidelines
- **POST requests:** JSON-encoded data
- **GET/DELETE requests:** URL-encoded data

**Common Response Codes:**
- **200:** Success
- **404:** Not Found
- **401:** Unauthorized
- **500:** Internal Server Error
