import { ethers } from "ethers";


const deltaApi= "https://api.dev.deltacrypt.net";

// This is for demonstration purposes only. You should never expose your API key in code!
const apiKey = "";


// Interfaces
interface RawTransactionResponse {
    raw_transaction: ethers.TransactionLike;
    topic: string;
}

interface RawInitiateTransactionResponse extends RawTransactionResponse {
    transaction_id: number;
}

interface BlockchainResponse {
    success: boolean;
    tracking_id: string;
}

interface GenericResponse {
    success: boolean;
}


// Example main
async function main() {
    // Setup
    const apiKeyId = 3;
    const accountId = 1004;
    const wallet = await setup(apiKeyId, accountId);

    // Get the raw transaction
    const senderWalletAddress = wallet.address;
    const amount = 42;
    const note = "Hello World!";
    const rawTransactionResponse = await getRawAndInitiateDeposit(senderWalletAddress, amount, note);
    console.log("Raw Transaction Response: ", rawTransactionResponse);

    // Sign the transaction
    const signedTransaction = await wallet.signTransaction(rawTransactionResponse.raw_transaction);
    console.log("Signed Transaction: ", signedTransaction);

    // Send the signed transaction to the blockchain
    const blockchainResponse = await sendSignedTransaction(signedTransaction, rawTransactionResponse.topic);
    console.log("Blockchain Response: ", blockchainResponse);
}

main();


// Setup
async function setup(apiKeyId: number, accountId: number) {
    // Gnerate a new wallet
    const wallet = ethers.Wallet.createRandom();
    console.log("Wallet Address: ", wallet.address);
    console.log("Wallet Private Key: ", wallet.privateKey);

    // You can also use an existing wallet (from the private key)
    const existingWallet = new ethers.Wallet(wallet.privateKey);
    console.log("Wallet Address: ", existingWallet.address);


    // Link the api key to the wallet
    const response = await linkApiKeyToAccount(apiKey, apiKeyId, accountId, wallet.address);
    console.log("Response: ", response);
    return wallet;
}


// Endpoints
// For this example we are using the API Key to authenticate the requests.
// This will require the API key to have the *link_api_key_to_account* permission for the target account.
async function linkApiKeyToAccount(
    apiKey: string,
    apiKeyId: number,
    accountId: number,
    walletAddress: string
) {
    return await extractInterface<GenericResponse>(
        fetch(deltaApi + "/account/link-api-key", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-KEY": apiKey
            },
            body: JSON.stringify({
                api_key_id: apiKeyId,
                account_id: accountId,
                wallet_address: walletAddress
            })
        })
    );
}

async function sendSignedTransaction(signedTransaction: string, topic: string) {
    return await extractInterface<BlockchainResponse>(
        fetch(deltaApi + "/blockchain/signed-transaction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                transaction_bytes: signedTransaction,
                topic: topic
            })
        })
    );
}

async function getRawAndInitiateDeposit(senderWalletAddress: string, amount: number, note: string) {
    return await extractInterface<RawInitiateTransactionResponse>(
        fetch(deltaApi + "/transaction/initiate-deposit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sender_wallet_address: senderWalletAddress,
                amount: amount,
                note: note
            })
        })
    );
}



// Utility
export async function extractInterface<T>(res: Promise<Response>): Promise<T> {
    const response = await res;
    if (response.ok) {
        return await response.json() as T;
    } else {
        const errorResponse = await response.json();
        console.error("Error Response: ", errorResponse);
        throw new Error(JSON.stringify(errorResponse));
    }
}