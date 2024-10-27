# B2C

The process of sending money to a customer (or another business) encompasses the following:

- Check whether the transaction is possible (optional)
- Initiate the transaction
- Sign the raw blockchain transaction
- Submit the signed blockchain transaction
- Query the blockchain transaction (optional)
- Receive a callback when the transaction status changes (IPN)
- Query the transaction

## Check Transaction Possible

Before initiating a transaction, it is advisable to check whether the transaction will be possible to avoid more complex polling or callback logic. There are a number of reasons a transaction might fail:

- Insufficient account balance
- Limits exceeded
- Transaction amount too low
- Account suspended or closed
- User not whitelisted

> **Note**: Insufficient spending allowances do not prevent the transaction from occurring; rather, the transaction will require approval, which will, in turn, reflect in the state of the transaction.

### `GET /transaction/transfer-possible`

**Request Parameters**

- `sender_wallet_address`: *string*
- `amount`: *number*
- `transaction_type`: *string*
- `recipient_username`: *Optional[string]*
- `recipient_account_id`: *Optional[number]*

The `sender_wallet_address` must be linked to an account.

> **Either** the `recipient_username` **or** `recipient_account_id` (or both) must be provided. If only the `recipient_username` is provided, the recipient account will be assumed to be the user's personal account. If both the `recipient_username` and `recipient_account_id` are provided, the `recipient_username` will be stored on the database in addition to the account.

**Example Response**
```json
{
    "possible": true,
    "sender_account_id": 1004,
    "fee": 0
}
```

or, alternatively, when the transfer is not possible

```json
{
    "possible": false,
    "error_name": "ERR_NOT_ENOUGH_BALANCE",
    "error_arguments": [
        "1004",
        "446370000000000000000",
        "5000000000000000000000"
    ]
}
```

---

## Initiate Transactions

### `GET /transaction/initiate-transfer`

**Request Parameters**

- `sender_wallet_address`: *string*
- `amount`: *number*
- `note`: *Optional[string]*
- `sender_till_id`: *Optional[number]*
- `recipient_username`: *Optional[string]*
- `recipient_account_id`: *Optional[number]*
- `recipient_till_id`: *Optional[number]*
- `transaction_type`: *string*
- `source_of_funds`: *Optional[string]*

**Example Response**

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
    "topic": "initiateTransfer",
    "transaction_id": 166
}
```

---

## Sign the Transaction

The next step involves signing the `raw_transaction` returned by the `GET /transaction/initiate-transfer` endpoint. The customer may use any of the available libraries that provide Ethereum functions.

- **JavaScript / TypeScript**
    - [ethers.js](https://github.com/ethers-io/ethers.js/)
    - [web3.js](https://github.com/ethereum/web3.js/)

- **Python**
    - [web3.py](https://github.com/ethereum/web3.py)
    - [eth-account](https://github.com/ethereum/eth-account)

- **Go**
    - [go-ethereum (geth)](https://github.com/ethereum/go-ethereum)
    - [ethers (for Go)](https://github.com/libs4go/ethers)

- **Java**
    - [web3j](https://github.com/web3j/web3j)

- **C#**
    - [Nethereum](https://github.com/Nethereum/Nethereum)

- **Ruby**
    - [ethereum.rb](https://github.com/EthWorks/ethereum.rb)

- **Swift (iOS)**
    - [web3.swift](https://github.com/Boilertalk/Web3.swift)

- **Rust**
    - [ethers-rs](https://github.com/gakonst/ethers-rs)
    - [web3-rs](https://github.com/tomusdrw/rust-web3)


---

## Submit the Signed Transaction

Once the transaction is signed, it needs to be submitted to the blockchain. Transactions are processed asynchronously but the order of transactions is preserved.

### `POST /blockchain/signed-transaction`

**Request Parameters**

- `transaction_bytes`: *string*
- `topic`: *string*

Use the `topic` that was returned from the `GET /transaction/initiate-transfer` endpoint.

**Example Response**

```json
{
    "success": true,
    "tracking_id": 214
}
```

---

### `GET /blockchain/transaction-status`

Optionally, the client can poll the status of the blockchain transaction. A blockchain transaction can either be `pending`, `failed`, or `succeeded`.

**Request Parameters**

- `transaction_id`: *string*

**Example Response**

```json
{
    "blockchain_transaction_status": "failed"
}
```

---

### `GET /blockchain/transaction/error-message`

If the blockchain transaction failed, the customer can retrieve more information on the failure reason.

**Request Parameters**

- `transaction_id`: *string*

**Example Response**

```json
{
    "error_message": "{\n  \"fragment\": {\n    \"type\": \"error\",\n    \"inputs\": [\n      {\n 
    \"name\": \"user\",\n        \"type\": \"address\",\n        \"baseType\": \"address\",\n    
    \"components\": null,\n        \"arrayLength\": null,\n        \"arrayChildren\": null\n  
    }\n    ],\n    \"name\": \"ERR_USER_NOT_WHITELISTED\"\n  },\n  \"name\":
    \"ERR_USER_NOT_WHITELISTED\",\n \"args\": [\n    
    \"0x2B5AD5c4795c026514f8317c7a215E218DcCD6cF\"\n  ],\n  \"signature\": 
    \"ERR_USER_NOT_WHITELISTED(address)\",\n  \"selector\": \"0x675037d5\"\n}"
}
```

---

Finally, you can wait for the IPN and query the transaction as described in the IPN and transaction querying sections.
