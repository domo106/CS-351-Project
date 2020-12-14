"""Handles JSON encoding/decoding"""
import json
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import struct

def json_decode(encoded_data):
    """Takes encoded data and converts to dictionary"""
    json_string = encoded_data.decode()
    data_dict = json.loads(json_string)
    return data_dict

def json_encode(data_dict):
    """Takes dictionary and converts to encoded data"""
    json_string = json.dumps(data_dict)
    encoded_data = json_string.encode()
    return encoded_data

def generate_keys():
    """
    Generates a public/private key pair
    And a session key
    Returns them in a tuple
    Tuple contains binary strings
    """
    # placeholder_keys = ("Public_Key","Private_Key")
    private_key = RSA.generate(2048)
    private_string = private_key.export_key()

    public_key = private_key.publickey()
    public_string = public_key.export_key()

    session_key = get_random_bytes(16)

    key_strings = (private_string, public_string, session_key)
    return key_strings

def encrypt_message(text, keys):
    """
    Takes plaintext message, and dict of keys as input
    Keys should contain my_session_key and peer_public_key
    Returns Encrypted Session Key, Nonce, Tag, Ciphertext
    In a dict
    """
    peer_public_key = keys["peer_public_key"]
    my_session_key = keys["my_session_key"]

    encoded_text = text.encode("utf-8")

    cipher_rsa = PKCS1_OAEP.new(peer_public_key)
    enc_session_key = cipher_rsa.encrypt(my_session_key)

    cipher_aes = AES.new(my_session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(encoded_text)
    print("Got ciphertext:", ciphertext)
    return_data = {
        "encrypted_session_key" : enc_session_key,
        "nonce" : cipher_aes.nonce,
        "tag" : tag,
        "ciphertext" : ciphertext,
    }
    #print("Sending Data in dict:",return_data)
    return return_data

def decrypt_message(data_dict, keys):
    """
    Takes Encrypted Session Key, Nonce, Tag, Ciphertext,
    In a dict. And dict of keys as input
    Keys should contain my_private_key
    Returns plaintext message
    """
    encrypted_session_key = data_dict["encrypted_session_key"]
    nonce = data_dict["nonce"]
    tag = data_dict["tag"]
    ciphertext = data_dict["ciphertext"]
    my_private_key = keys["my_private_key"]
    # Decrypt session key
    cipher_rsa = PKCS1_OAEP.new(my_private_key)
    session_key = cipher_rsa.decrypt(encrypted_session_key)

    # Decrypt Message
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    encoded_message = cipher_aes.decrypt_and_verify(ciphertext, tag)
    text = encoded_message.decode("utf-8")
    return text
"""
keys = generate_keys()
key_dict = {
    "my_private_key": RSA.import_key(keys[0]),
    "peer_public_key": RSA.import_key(keys[1]),
    "my_session_key": keys[2],
}
for key in key_dict:
    print("Generated key {} of type {}".format(key, key_dict[key]))
message = "Hello World!"
data = encrypt_message(message, key_dict)

message = decrypt_message(data, key_dict)
print(message)
"""
