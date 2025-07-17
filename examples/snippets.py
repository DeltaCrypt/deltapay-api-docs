import asyncio
from typing import Any
from web3 import Web3
from httpx import AsyncClient, Response
from pydantic import BaseModel


# Package versions for requirements.txt
# web3==7.8.0
# httpx==0.28.1
# pydantic==2.10.6

# Python 3.12.7

delta_api = "https://api.dev.deltacrypt.net"
api_key = "NWSbVd_RGfAcFKhT9p5grVKrl7p6cD_RyEM_Q-ftH30"  # Never expose API keys in production!


###### Data Models
class GenericResponse(BaseModel):
    success: bool = True


class BlockchainResponse(GenericResponse):
    tracking_id: int


class RawTransactionResponse(BaseModel):
    raw_transaction: dict[str, Any]
    topic: str


class RawInitiateTransactionResponse(RawTransactionResponse):
    transaction_id: int


class BlockchainTransactionStatusResponse(BaseModel):
    blockchain_transaction_status: str
    

###### Utility Stuff
class CustomException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
    
    def __str__(self):
        return "Custom error: " + self.message
    

def checkResponse(response: Response):
    try:
        response_data = response.json()
    except Exception:
        response_data = response.text  # Fallback for non-JSON responses

    if response.status_code != 200:
        raise CustomException(
            message=str(response_data),  # Ensure it's a string
            status_code=response.status_code
        )


# Helper that translates the custom raw_transaction format to the format expected by web3.py.
def translate_transaction(raw_transaction):
    # Convert chainId from string to integer
    raw_transaction['chainId'] = int(raw_transaction['chainId'])

    # Convert gasLimit from hex string to integer
    raw_transaction['gas'] = int(raw_transaction['gasLimit'], 16)
    del raw_transaction['gasLimit']  # Remove the old gasLimit key

    # Ensure gasPrice is an integer (it's already fine if 0)
    raw_transaction['gasPrice'] = int(raw_transaction['gasPrice'])

    # Remove 'type' if it's a legacy transaction (type 0)
    if 'type' in raw_transaction and raw_transaction['type'] == 0:
        del raw_transaction['type']

    # Return the modified transaction
    return raw_transaction


###### API calls
# If the api key is already linked to the account, the wallet address will be updated.
async def link_api_key_to_account(api_key: str, api_key_id: int, account_id: int, wallet_address: str) -> GenericResponse:
    async with AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url=f"{delta_api}/account/link-api-key",
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": api_key
            },
            json={
                "api_key_id": api_key_id,
                "account_id": account_id,
                "wallet_address": wallet_address
            }
        )
        checkResponse(response)
        return GenericResponse()


async def send_signed_transaction(signed_transaction: str, topic: str) -> BlockchainResponse:
    async with AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url=f"{delta_api}/blockchain/signed-transaction",
            json={
                "transaction_bytes": signed_transaction,
                "topic": topic
            }
        )
        checkResponse(response)
        return BlockchainResponse(**response.json())


async def get_raw_and_initiate_deposit(sender_wallet_address: str, amount: int, note: str) -> RawInitiateTransactionResponse:
    async with AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url=f"{delta_api}/transaction/initiate-deposit",
            json={
                "sender_wallet_address": sender_wallet_address,
                "amount": amount,
                "note": note
            }
        )
        checkResponse(response)
        return RawInitiateTransactionResponse(**response.json())
    
    
async def get_blockchain_transaction_status(transaction_id: int):
    async with AsyncClient(timeout=30.0) as client:
        response = await client.get(
            url=f"{delta_api}/blockchain/transaction-status",
            params={"transaction_id": transaction_id}
        )
        # Note that this endpoint returns a 404 if the transaction is not found
        # --> You might want to handle this case differently instead of just raising an exception in checkResponse
        checkResponse(response)
        return BlockchainTransactionStatusResponse(**response.json())


###### Main Functions
async def setup(api_key_id: int, account_id: int):
    w3 = Web3()
    account = w3.eth.account.create()
    print("Wallet Address:", account.address)
    print("Wallet Private Key:", account._private_key.hex())
    
    response = await link_api_key_to_account(api_key, api_key_id, account_id, account.address)
    print("Linking successful:", response.success)
    return account


# Function that async polls the blockchain transaction status for a given transaction ID
async def poll_transaction_status(transaction_id: int):
    max_attempts = 10
    attempts = 0
    polling = True
    final_status = None
    
    while polling and attempts < max_attempts:
        response = await get_blockchain_transaction_status(transaction_id)
        final_status = response.blockchain_transaction_status
        print("Transaction status:", final_status)
        
        if final_status == "pending":
            attempts += 1
            await asyncio.sleep(1)
        else:
            polling = False
    
    print("Final Transaction Status:", final_status)


async def main():
    wallet = await setup(
        api_key_id=2,
        account_id=28
    )
    private_key = wallet._private_key.hex()
    
    # Alternatively, get the wallet from the private key (this is what you will do in practice once its set up once)
    #private_key = "adc2a203b13545e04d767dd2eed4047a3a00834868822202ba7b85aa9a6221e9" # replace with what is printed in the setup function
    wallet = Web3().eth.account.from_key(private_key)
    
    raw_transaction_response = await get_raw_and_initiate_deposit(
        sender_wallet_address=wallet.address,
        amount=12,
        note="Hello World!"
    )
    print("Raw Transaction Response:", raw_transaction_response)

    # If you don't want to use the Web3 package for some reason (e.g. since its really overkill for this)
    # Feel free to have a look at the eth_account package (see example siging function in apendix)
    signed_transaction = "0x" + wallet.sign_transaction(translate_transaction(raw_transaction_response.raw_transaction)).raw_transaction.hex()
    print("Signed Transaction:", signed_transaction)

    blockchain_response = await send_signed_transaction(signed_transaction, raw_transaction_response.topic)
    print("Blockchain Response:", blockchain_response)
    
    # Polling is optional since in most cases you will be updated through the callback
    # However the callback is concirend with the whole transaction lifecycle, while the polling is only for the blockchain transaction status
    # It is important to note that the blockchain transaction status is not the same as the transaction status
    # E.g., initiating a deposit entails one blockchain transaction, approving or finalising the deposit entails another
    await poll_transaction_status(blockchain_response.tracking_id)


if __name__ == "__main__":
    asyncio.run(main())


###### Appendix
# Alternative library for signing transactions
# from eth_account import Account
# def sign_raw_tx(raw_transaction_response: RawTransactionResponse, private_key: str):
#     # Make sure the private key has the 0x prefix
#     sender_wallet = Account.from_key(private_key)
#     signed_transaction = sender_wallet.sign_transaction(translate_transaction(raw_transaction_response.raw_transaction))
#     return "0x" + signed_transaction.raw_transaction.hex()

