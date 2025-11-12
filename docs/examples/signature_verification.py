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
    
    
    
def main():
    # The payload as JSON (note: null in JSON becomes None in Python after json.loads)
    json_payload = r'''
    {
        "transaction_id": 965,
        "transaction_type": "entertainment",
        "transaction_status": "succeeded",
        "initialisation_time": "2025-10-06T12:49:26.454195",
        "settled_time": "2025-10-06T12:49:31.640124",
        "note": "Deposit To MulaSport",
        "metadata": "d33be0dd-27ec-4f4f-aefc-4efe3b0ef3b2",
        "source_of_funds": null,
        "bank_account": null,
        "sender_account_id": 83,
        "sender_account_name": "Personal",
        "sender_name": "Dayni Test (@dayni)",
        "sender_till_name": null,
        "sender_phone_country_dialcode": null,
        "sender_phone_number": null,
        "recipient_account_id": 26,
        "recipient_account_name": "main",
        "recipient_name": "MulaSport",
        "recipient_till_name": null,
        "recipient_phone_country_dialcode": null,
        "recipient_phone_number": null,
        "amount": 60,
        "cashback_received": 0,
        "cashback_spent": 0,
        "fee": 0.3,
        "commission_amount": 0,
        "direction": "in",
        "payment_request_id": 367,
        "signature": "aEWJyua0ze2qAfKX1/PzjtRck2axXFVeBX3BawrbPNAdrGcqf2A6UOV8tX3f9MyUhb2PPPKyhtILouq3Uc9cKvXLT6CN6gla6cN0mdoybmxKfGlcMEar7SXUcMd0Z9FoRccw4jRq/+NES2KNPCUe3IdUyTMp8YEoSnS1hsZntL/MW7k8sqUeZX+nkKdWyHbFeZtSvjKI5SGJ2D1D4v3L3qRhP80TxwB3zXkzEAeutEZBdgKICxE3dK8ZieZLpK2TKm30uSgurGMOhM3cSFHWfOLApuvHpuEjSDrZokJUGx9WlNGqaIdc6fCa2Fo9PYxQ9vc9W20V57O1AlE3WXtZpA=="
    }
    '''

    # Public key with literal "\n" which we convert to real newlines
    public_key_pem_escaped = (
        "-----BEGIN PUBLIC KEY-----\\n"
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwnqD5ZmC0rtpHDc1G+Il\\n"
        "oYj/gbwC6aUZ0v8Y5MM2YI5WcYSlaVSGUhPy1u7Hwgu4URwQseMaXgdJklbTf2sy\\n"
        "xQsMONdo6AQIlyzNKjcozdpMMA9fkGgA3TR1CSyl06TMia2+ipZGQ5glpegVU6Co\\n"
        "VDCLJNzpSbJ9S5qL5RQ25PJm5GxAgaupvZoaGZxzicmjsRZ3oKUgjSrN9uaikT68\\n"
        "LLrqRCjOeCqH5DSXbSLWcd49Tzwx+gU3e/4URRTgGnVz39AmH38TKKawX4H05Agq\\n"
        "jT7cmfTC5SDUo3wxs5sQk+4qODrscHWKlThzs4wIiCF2oGAkphOqgoi21eKivAZS\\n"
        "cQIDAQAB\\n"
        "-----END PUBLIC KEY-----\\n"
    )
    public_key_pem = public_key_pem_escaped.replace("\\n", "\n")

    data = json.loads(json_payload)

    ok = verify_signature(public_key_pem, data)
    print("Verified:", ok)


if __name__ == "__main__":
    main()