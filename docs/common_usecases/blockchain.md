# Interacting with the Blockchain

The process for interacting with the blockchain is consistent across all transaction types:

1. **Get** the raw Ethereum transaction object.
2. **Sign** the raw blockchain transaction.
3. **Submit** the signed blockchain transaction.
4. **Query** the blockchain transaction (optional).

In some cases, the endpoint returning the raw transaction also performs additional setup (for example, [`/transaction/initiate-deposit`](https://api.dev.deltacrypt.net/docs#/transactions/initiate_deposit_transaction_initiate_deposit_post) both creates the database entry and prepares the blockchain transaction).

For frequently used operations, shortcut endpoints are provided.
These endpoints handle signing internally if the private key is supplied, reducing the process to a **single HTTP request** (e.g. [`POST /transaction/send-transfer`](https://api.dev.deltacrypt.net/docs#/transactions/send_transfer_transaction_send_transfer_post)).

> **Note:** When using endpoints that accept a private key directly, security relies on standard **TLS encryption**. The private keys sent in this way are **never stored** on DeltaPay servers.

### Difference Between Transaction and Blockchain Transaction

A **transaction** in DeltaPay refers to the high-level payment record tracked in the DeltaPay database (for example, a deposit or transfer).
A **blockchain transaction** is the corresponding on-chain event that executes the transfer of tokens or smart-contract function.

One DeltaPay transaction may involve multiple blockchain transactions — for example,
a deposit could include both an *initialisation* and a *finalisation* transaction.
Blockchain-level errors are reflected separately via the blockchain transaction status and error-message endpoints.


## 1. Getting the Raw Transaction

The raw transaction describes what will be executed on the blockchain.
It includes fields such as `to`, `data`, `chainId`, `gasLimit`, and `nonce`.

**Example response structure:**

```json
{
  "raw_transaction": {
    "from": "0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf",
    "to": "0x52A816dB82157a5f4b2c4Fb5Be745AC4103Db674",
    "nonce": 0,
    "chainId": "1337",
    "data": "0x21d43aaf000000000.....",
    "gasLimit": "0x1ffffffffffffe",
    "gasPrice": 0,
    "type": 0
  },
  "topic": "finaliseTransfer"
}
```

You can now sign the `raw_transaction` using any Ethereum-compatible library. Once signed, it should be submitted to the blockchain using the returned `topic`.


## 2. Signing the Raw Transaction

Signing transforms the unsigned JSON transaction into a signed, broadcastable payload.
The `raw_transaction` must be signed using the private key corresponding to the `sender_wallet_address`. Any Ethereum-compatible signing library can be used.

### Recommended Libraries

**JavaScript / TypeScript**

* [ethers.js](https://github.com/ethers-io/ethers.js)
* [web3.js](https://github.com/ethereum/web3.js)

**Python**

* [web3.py](https://github.com/ethereum/web3.py)
* [eth-account](https://github.com/ethereum/eth-account)

**Other Supported Languages**

* Go → [go-ethereum](https://github.com/ethereum/go-ethereum)
* Java → [web3j](https://github.com/web3j/web3j)
* C# → [Nethereum](https://github.com/Nethereum/Nethereum)
* Swift → [web3.swift](https://github.com/Boilertalk/Web3.swift)
* Rust → [ethers-rs](https://github.com/gakonst/ethers-rs)

Below are short code examples for the most common environments.
The full runnable examples (including API setup, error handling, and polling) are available in the [Python Example](../examples/snippets.py) and [TypeScript Example](../examples/snippets.ts) sections.

### Python Example (using `web3.py`)

```python
from web3 import Web3

# raw_transaction is what you received from the initiate endpoint
def translate_transaction(raw_transaction):
    raw_transaction['chainId'] = int(raw_transaction['chainId'])
    raw_transaction['gas'] = int(raw_transaction['gasLimit'], 16)
    del raw_transaction['gasLimit']
    raw_transaction['gasPrice'] = int(raw_transaction['gasPrice'])
    if raw_transaction.get('type') == 0:
        del raw_transaction['type']
    return raw_transaction

w3 = Web3()
wallet = w3.eth.account.from_key("YOUR_PRIVATE_KEY_HERE")

signed = wallet.sign_transaction(translate_transaction(raw_transaction))
signed_transaction = "0x" + signed.raw_transaction.hex()

print("Signed Transaction:", signed_transaction)
```

This produces a hex-encoded signed transaction string that you can now submit to the blockchain.


### JavaScript / TypeScript Example (using `ethers.js`)

```typescript
import { ethers } from "ethers";

// raw_transaction is what you received from the initiate endpoint
const wallet = new ethers.Wallet("YOUR_PRIVATE_KEY_HERE");
const signedTransaction = await wallet.signTransaction(raw_transaction);

console.log("Signed Transaction:", signedTransaction);
```

Both examples generate a `signedTransaction` string which should be sent to the `/blockchain/signed-transaction` endpoint, together with the `topic` value returned earlier.


## 3. Submitting the Signed Transaction

[`POST /blockchain/signed-transaction`](https://api.dev.deltacrypt.net/docs#/blockchain/send_signed_transaction_blockchain_signed_transaction_post)

**Request Parameters**

* `transaction_bytes`: *string* — the signed transaction hex string
* `topic`: *string* — the topic returned by the raw transaction endpoint

**Example Request**

```json
{
  "transaction_bytes": "0xf86b80843b9aca0082520894...",
  "topic": "finaliseTransfer"
}
```

**Example Response**

```json
{
  "success": true,
  "tracking_id": 214
}
```

Use the `tracking_id` to query blockchain transaction status or correlate with internal transaction logs.


## 4. Querying Blockchain Transaction Status

You can query the blockchain transaction status directly, or rely on the IPN callback to notify your system of updates.

### Get Blockchain Transaction Status

[`GET /blockchain/transaction-status`](https://api.dev.deltacrypt.net/docs#/blockchain/get_transaction_status_blockchain_transaction_status_get)

**Request Parameters**

* `transaction_id`: *string* — The blockchain transaction id

**Example Response**

```json
{
  "blockchain_transaction_status": "succeeded"
}
```

### Get Blockchain Transaction Error Message

[`GET /blockchain/transaction/error-message`](https://api.dev.deltacrypt.net/docs#/blockchain/get_transaction_error_message_blockchain_transaction_error_message_get)

If the transaction failed, this endpoint provides the decoded smart-contract error for debugging.

**Example Response**

```json
{
  "error_message": "{\n  \"name\": \"ERR_USER_NOT_WHITELISTED\",\n  \"args\": [\"0x2B5AD5c4795c026514f8317c7a215E218DcCD6cF\"]\n}"
}
```