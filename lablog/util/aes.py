from Crypto.Cipher import AES
import random
import os

MODE = AES.MODE_CBC
BLOCK_SIZE = 16
INTERRUPT = u'\u0000'
PAD = u'\u0000'

def pad(st):
    st = ''.join([st, config.INTERRUPT])
    st_len = len(st)
    rem_len = config.BLOCK_SIZE-st_len
    padding_len = rem_len%config.BLOCK_SIZE
    padding = config.PAD*padding_len
    final_st = ''.join([st, padding])
    return final_st

def encrypt(st, key):
    st = pad(st)
    IV = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    CIPHER = AES.new(key, MODE, IV)
    res = CIPHER.encrypt(st)
    res = IV+res
    return base64.urlsafe_b64encode(res)

def decrypt(st, key):
    SIV = bytearray(st[:16])
    IV = buffer(SIV)
    CIPHER = AES.new(key, MODE, IV)
    res = CIPHER.decrypt(st[16:])
    return res.split("\x00")[0]

def generate_key():
    return os.urandom(16)
