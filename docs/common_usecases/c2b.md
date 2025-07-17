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

### PHP

#### Requirements:

* **phpseclib v3** installed via Composer (`composer require phpseclib/phpseclib:^3.0`)
* **ext-json** enabled (for `json_encode`/`json_decode`)
* **GMP** or **BCMath** PHP extension (php-gmp or php-bcmath)
* **ext-openssl** enabled (optional but recommended for performance)
* **PHP 7.2+** (phpseclib3 works on 5.6+, but PSS+SHA-256 is most reliable on 7.2+)
* A valid **RSA public key** in PEM format matching the signer’s key


```php title="verify.php" linenums="1"

<?php
// php_test.php

require __DIR__ . '/vendor/autoload.php';

use phpseclib3\Crypt\PublicKeyLoader;
use phpseclib3\Crypt\RSA;

// 1) Your full callback data, including the signature
$callbackData = [
    'transaction_id'                   => 397,
    'transaction_type'                 => 'education',
    'transaction_status'               => 'succeeded',
    'initialisation_time'              => '2024-10-26T19:07:12.872556',
    'settled_time'                     => '2024-10-26T19:07:18.856786',
    'note'                             => 'bro',
    'metadata'                         => null,
    'source_of_funds'                  => '',
    'bank_account'                     => null,
    'sender_account_id'                => 1014,
    'sender_account_name'              => 'New 3',
    'sender_name'                      => 'DeltaPay',
    'sender_till_name'                 => null,
    'sender_phone_country_dialcode'    => null,
    'sender_phone_number'              => null,
    'recipient_account_id'             => 1001,
    'recipient_account_name'           => 'Personal',
    'recipient_name'                   => 'adrian',
    'recipient_till_name'              => null,
    'recipient_phone_country_dialcode' => null,
    'recipient_phone_number'           => null,
    'amount'                           => 7,
    'cashback_received'                => 0,
    'cashback_spent'                   => 0,
    'fee'                              => 0,
    'commission_amount'                => 0,
    'signature'                        => 'aY59ZtcOebh8tPrHACHrAhE7k0IoLvXha5I7jPdNj1niSSktaXScmI6mOUztFEk5LEYSUiYyDYvAK/qqt4c4hLYX5KjSZR1IuA7y9mlLn4O/WFyqTQ7vweKqFuQrpptpMhxupf7Jb9JI/dr02+txGF0BgA8q/4C9cqJIGiN8wncMuMUm0rg7DGRxwEWbc5Odn9IRyGQA3j3cU0uPDQZ0z12ucFs5AtspfsrBFdbKsV66eb1PSHSGUe0AF2cIZEqk7r5JwU4EAQCLYoShrg6J2NZdzlVXCFZk2+l20LXSCdH9pR6ZDvBSOLUhpwavHfDs27IEvtasMxvXx7B1OEHBoA=='
];

// 2) Your RSA public key
$publicKeyPem = <<<'KEY'
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw4iXQZfRMpjTOOgLEaBl
xmYvbE8RbbfUq6ROQUrzTE1+QkAwZCL8VDdBenaNXrndjBK+2hh9sA5hQGzqlCgY
MRvkaDtLUuHyo5YFSfJ8z4WHMoS6/B/t9rc+56I05tDabcMgPYAU4V9M1jYZ7Aie
LfLQfKwA96EewBPoGMJaespF4NVMh/UmOkzIj3uidueiZjG9ef7vYJrha7Y7f6x4
JjA7Dt5eh9SzF8ck9fsIjca/e/KwJhKlRZ+tMnkFSU/b4Sds90pGl1Inneqp1oHs
a/PpV9BYM8rvEQdvs6ifObLIOCPw+zQdcFKW/FbPWq016ZVMy0iT+Lmh7sB5bORk
2wIDAQAB
-----END PUBLIC KEY-----
KEY;

// --- extract & decode the signature ---
if (!isset($callbackData['signature'])) {
    echo "? signature field missing\n";
    exit(1);
}
$sigB64    = $callbackData['signature'];
unset($callbackData['signature']);
$signature = base64_decode($sigB64);

// --- sort keys like Python sort_keys=True ---
ksort($callbackData);

// --- build the JSON payload with “, ” and “: ” separators ---
$parts = [];
foreach ($callbackData as $k => $v) {
    $jsonKey   = json_encode($k, JSON_UNESCAPED_UNICODE);
    $jsonValue = $v === null
        ? 'null'
        : json_encode($v, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    $parts[] = "{$jsonKey}: {$jsonValue}";
}
$payload = '{' . implode(', ', $parts) . '}';

// Show it
echo "Serialized data for verification:\n{$payload}\n\n";

// --- load key & configure PSS+SHA256 ---
$key = PublicKeyLoader::load($publicKeyPem)
    ->withHash('sha256')
    ->withMGFHash('sha256')
    ->withPadding(RSA::SIGNATURE_PSS);

// compute Python’s MAX_LENGTH salt (keyBytes - hashLen - 2)
$keyBits  = $key->getLength();                   // e.g. 2048
$keyBytes = intdiv($keyBits, 8);                 // e.g. 256
$hashLen  = strlen(hash('sha256', '', true));    // 32
$saltLen  = $keyBytes - $hashLen - 2;            // 256-32-2 = 222

// apply it
$rsa = $key->withSaltLength($saltLen);

// verify
if ($rsa->verify($payload, $signature)) {
    echo "? Signature verification successful.\n";
    exit(0);
} else {
    echo "? Signature verification failed.\n";
    exit(1);
}

```

### C#

#### Requirements:

* **.NET 6.0 SDK** (or later)
* **BouncyCastle.NetCore** installed via NuGet
* **System.Text.Json** (Included in .NET Core 3.0+; used for key/value serialization.)

``` c#

using System.Text;
using System.Text.Json;
using Org.BouncyCastle.Crypto;
using Org.BouncyCastle.Crypto.Digests;
using Org.BouncyCastle.Crypto.Engines;
using Org.BouncyCastle.Crypto.Parameters;
using Org.BouncyCastle.Crypto.Signers;
using Org.BouncyCastle.OpenSsl;

class Program
{
    static int Main()
    {
        // 1) Build your callback data dictionary, signature last
        var callbackData = new Dictionary<string, object>
        {
            ["transaction_id"] = 397,
            ["transaction_type"] = "education",
            ["transaction_status"] = "succeeded",
            ["initialisation_time"] = "2024-10-26T19:07:12.872556",
            ["settled_time"] = "2024-10-26T19:07:18.856786",
            ["note"] = "bro",
            ["metadata"] = null,
            ["source_of_funds"] = "",
            ["bank_account"] = null,
            ["sender_account_id"] = 1014,
            ["sender_account_name"] = "New 3",
            ["sender_name"] = "DeltaPay",
            ["sender_till_name"] = null,
            ["sender_phone_country_dialcode"] = null,
            ["sender_phone_number"] = null,
            ["recipient_account_id"] = 1001,
            ["recipient_account_name"] = "Personal",
            ["recipient_name"] = "adrian",
            ["recipient_till_name"] = null,
            ["recipient_phone_country_dialcode"] = null,
            ["recipient_phone_number"] = null,
            ["amount"] = 7,
            ["cashback_received"] = 0,
            ["cashback_spent"] = 0,
            ["fee"] = 0,
            ["commission_amount"] = 0,
            // signature must be the *last* key here so we can remove it cleanly
            ["signature"] = "aY59ZtcOebh8tPrHACHrAhE7k0IoLvXha5I7jPdNj1niSSktaXScmI6mOUztFEk5LEYSUiYyDYvAK/qqt4c4hLYX5KjSZR1IuA7y9mlLn4O/WFyqTQ7vweKqFuQrpptpMhxupf7Jb9JI/dr02+txGF0BgA8q/4C9cqJIGiN8wncMuMUm0rg7DGRxwEWbc5Odn9IRyGQA3j3cU0uPDQZ0z12ucFs5AtspfsrBFdbKsV66eb1PSHSGUe0AF2cIZEqk7r5JwU4EAQCLYoShrg6J2NZdzlVXCFZk2+l20LXSCdH9pR6ZDvBSOLUhpwavHfDs27IEvtasMxvXx7B1OEHBoA=="
        };

        // 2) Extract & decode the signature:
        if (!callbackData.TryGetValue("signature", out var sigObj) || sigObj is not string sigB64)
        {
            Console.WriteLine("? signature field missing");
            return 1;
        }
        callbackData.Remove("signature");
        byte[] signature = Convert.FromBase64String(sigB64);

        // 3) Sort keys lexicographically:
        var sorted = callbackData.OrderBy(kvp => kvp.Key, StringComparer.Ordinal);

        // 4) Reassemble JSON with exactly ": " and ", ":
        var parts = sorted.Select(kvp =>
        {
            string jsonKey = JsonSerializer.Serialize(kvp.Key);
            string jsonValue = kvp.Value is null
                ? "null"
                : JsonSerializer.Serialize(kvp.Value);
            return $"{jsonKey}: {jsonValue}";
        });
        string payload = "{" + string.Join(", ", parts) + "}";

        Console.WriteLine("Serialized data for verification:");
        Console.WriteLine(payload);
        Console.WriteLine();

        // 5) Load the RSA public key via BouncyCastle
        string publicKeyPem = @"
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw4iXQZfRMpjTOOgLEaBl
xmYvbE8RbbfUq6ROQUrzTE1+QkAwZCL8VDdBenaNXrndjBK+2hh9sA5hQGzqlCgY
MRvkaDtLUuHyo5YFSfJ8z4WHMoS6/B/t9rc+56I05tDabcMgPYAU4V9M1jYZ7Aie
LfLQfKwA96EewBPoGMJaespF4NVMh/UmOkzIj3uidueiZjG9ef7vYJrha7Y7f6x4
JjA7Dt5eh9SzF8ck9fsIjca/e/KwJhKlRZ+tMnkFSU/b4Sds90pGl1Inneqp1oHs
a/PpV9BYM8rvEQdvs6ifObLIOCPw+zQdcFKW/FbPWq016ZVMy0iT+Lmh7sB5bORk
2wIDAQAB
-----END PUBLIC KEY-----";

        AsymmetricKeyParameter bcPub;
        using (var reader = new System.IO.StringReader(publicKeyPem))
        {
            var pem = new PemReader(reader);
            bcPub = (AsymmetricKeyParameter)pem.ReadObject();
        }

        // 6) Calculate max salt length = keyBytes - hashLen - 2
        int keyBits = ((RsaKeyParameters)bcPub).Modulus.BitLength;
        int keyBytes = keyBits / 8;
        int hashLen = 32;               // SHA-256 output is 32 bytes
        int saltLen = keyBytes - hashLen - 2;

        // 7) Configure PSS verifier with max salt
        var verifier = new PssSigner(
            new RsaEngine(),
            new Sha256Digest(),
            saltLen
        );
        verifier.Init(false, bcPub);

        byte[] dataBytes = Encoding.UTF8.GetBytes(payload);
        verifier.BlockUpdate(dataBytes, 0, dataBytes.Length);

        bool ok = verifier.VerifySignature(signature);
        Console.WriteLine(ok
            ? "Signature verification successful."
            : "Signature verification failed.");

        return ok ? 0 : 1;
    }
}

```
