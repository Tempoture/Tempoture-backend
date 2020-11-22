from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii
import os

CRYPTO_KEY = pad((os.environ['CRYPTO_KEY']).encode('utf-8'), AES.block_size)
CRYPTO_IV = pad((os.environ['CRYPTO_IV']).encode('utf-8'), AES.block_size)

def _encrypt(plain_text, key, iv): 
    data_bytes = bytes(plain_text, 'utf-8')
    padded_bytes = pad(data_bytes, AES.block_size)
    AES_obj = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = AES_obj.encrypt(padded_bytes)
    cipher_text = binascii.hexlify(cipher_text)

    return cipher_text

def _decrypt(cipher_text, key, iv):
    cipher_text = binascii.unhexlify(cipher_text)
    AES_obj = AES.new(key, AES.MODE_CBC, iv)
    raw_bytes = AES_obj.decrypt(cipher_text)
    extracted_bytes = unpad(raw_bytes, AES.block_size)
    plain_text = extracted_bytes.decode('ascii')

    return plain_text
