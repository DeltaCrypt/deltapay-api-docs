# Scenario

The customer pays for a service using DeltaPay. The service provider is notified of updates regarding the transaction such as the success or failure of the payment.

For example, the process of paying for an item online might look something like this:

<!-- TODO: Add section on payment requests -->
1. The website generates a payment QR code encoding the amount, recipient, and reference (see [QR Code Specification](qr_code.md))
2. The user scans the QR code and the information is prefilled on the DeltaPay app
3. The user approves and sends the transaction
4. The IPN is sent to the registered callback(s) notifying the seller of an update regarding the payment.

<!-- > **Note**: We are working on a feature that will allow for prompting the customer to initiate via a notification sent to their device that, when clicked, will pre-fill the send money dialog. Until then, the user must enter the information manually. -->
> **Note**: We are working on supporting deep-links and payment request notifications as an alternative to QR code or manual input.

## Payment reference

There are two options for encoding a payment reference:

- **notes**: can be entered and edited by the user (max 200 characters)
- **metadata**: is not shown to the user

The are both arbitrary strings that can be included in the QR code and will be picked up by the DeltaPay app.

# Instant Payment Notification (IPN)

## Callback registration

To receive IPNs, the user must first register the base callback URL as described in the [Setup section](./setup.md#callback-registration).

<!-- - the signature that is returned
- viewing it
- shall we add a feature to re-generate (or simply delete and create new callback?) 
The keys are in PEM format
-->

The callback is triggered for all updates of the transaction status of transactions involving either the **sender or recipient account**.

 The callback URL format is as follows:

    base URL + /transaction/ipn


## Format

Below is an example of what the IPN looks like

```json
{
    "transaction_id": 398,
    "transaction_type": "rent",
    "transaction_status": "succeeded",
    "initialisation_time": "2024-10-26T20:43:15.515122",
    "settled_time": "2024-10-26T20:43:21.639949",
    "note": "hello",
    "metadata": null,
    "source_of_funds": "",
    "bank_account": null,
    "sender_account_id": 1014,
    "sender_account_name": "New 3",
    "sender_name": "DeltaPay",
    "sender_till_name": null,
    "sender_phone_country_dialcode": null,
    "sender_phone_number": null,
    "recipient_account_id": 1001,
    "recipient_account_name": "Personal",
    "recipient_name": "adrian",
    "recipient_till_name": null,
    "recipient_phone_country_dialcode": null,
    "recipient_phone_number": null,
    "amount": 6,
    "cashback_received": 0,
    "cashback_spent": 0,
    "fee": 0,
    "commission_amount": 0,
    "signature": "VMDnRnvRJVvTHu9HNgjsIWhlXOd1bYkPPsp23y3cVl3Tn7Zzlg7AJAy5654fld5U7XrhQbDd3Mj684WcFnpbRgeiRIQDBtEL2eLKO7ZHjC/jg0n0zVjE2TRfPACuiXsmR/pJG+8hPmABBqThGj2hE5SEBFD4WSlzgAcLA0ZxZWvtDu2FAUpN1B+FtMfCmxa4DmH/GPtVs+80c8hHX3KGt35iaBrwD66vhdEUrSaYEgFooRmS3K9dm+neOPHgIfXG60sv03Ru5EZDMKNQvalUlCdLUerjr3eoZPs4DkYZj2FhwBZOJPBh6SDmCgSUsKclvepd0hExXNsRwOsKsxDcuQ=="
}
```

## Signature verification

In order to verify that your callback has indeed been called by DeltaPay you must verify the signature that is included in the request. 

> **Note**: In the future, we will provide libraries for the most common languages to simplify this process. For now, please don't hesitate to contact us for a code snipped in your prefered language.

### Python
```py title="verify.py" linenums="1"
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import json
import base64

# param: public_key_pem: The signing_key linked to the callback
# param: data: The json data sent as the IPN
def verify_signature(public_key_pem: str, data: dict):
    public_key_pem_bytes = public_key_pem.encode('utf-8')
    public_key = serialization.load_pem_public_key(public_key_pem_bytes, backend=default_backend())
    
    # Ensure the public key is of RSA type
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError("The provided public key is not an RSA key. Please ensure you are loading an RSA public key.")
    
    
    encoded_signature = data.pop("signature")
    signature = base64.b64decode(encoded_signature)
    data_to_verify = json.dumps(data, sort_keys=True).encode('utf-8')
    
    try:
        public_key.verify(
            signature,
            data_to_verify,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Signature verification successful.")
        return True
    except Exception as e:
        print("Signature verification failed:", e)
        return False
```

### JavaScript

```js title="verify.js" linenums="1"
const crypto = require('crypto');

// param: public_key_pem: The signing_key linked to the callback
// param: data: The json data sent as the IPN
function verifySignature(publicKeyPem, data) {
    // Extract and decode the signature
    const signature = Buffer.from(data.signature, 'base64');
    delete data.signature;

    // Sort and construct JSON string matching Python's exact whitespace output
    const sortedData = Object.keys(data)
        .sort()
        .reduce((obj, key) => {
            obj[key] = data[key];
            return obj;
        }, {});

    const formattedData = '{' + Object.entries(sortedData)
        .map(([key, value]) => {
            const jsonKey = JSON.stringify(key);
            const jsonValue = value === null ? 'null' : JSON.stringify(value);
            return `${jsonKey}: ${jsonValue}`;
        })
        .join(', ') + '}';

    console.log("Serialized data for verification (formatted):", formattedData);

    // Create verification instance and feed in formatted data
    const verify = crypto.createVerify('sha256');
    verify.update(Buffer.from(formattedData, 'utf-8'));
    verify.end();

    const isVerified = verify.verify(
        { key: publicKeyPem, padding: crypto.constants.RSA_PKCS1_PSS_PADDING },
        signature
    );

    console.log(isVerified ? "Signature verification successful." : "Signature verification failed.");
    return isVerified;
}

```
