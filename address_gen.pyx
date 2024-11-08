# address_gen.pyx
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
import coincurve
import base58
import hashlib
from Crypto.Hash import RIPEMD160

def generate_addresses_cython(batch_size=1000):
    """
    Generate a batch of Bitcoin addresses.

    :param batch_size: Number of addresses to generate in this batch.
    :return: List of tuples containing (compressed_pubkey, bitcoin_address).
    """
    addresses = []
    for _ in range(batch_size):
        # Step 1: Generate private key using coincurve for speed
        private_key = coincurve.PrivateKey()

        # Step 2: Generate compressed public key
        compressed_pubkey = private_key.public_key.format(compressed=True).hex()

        # Step 3: Generate Bitcoin address
        sha256_bpk = hashlib.sha256(bytes.fromhex(compressed_pubkey)).digest()

        ripemd160 = RIPEMD160.new()
        ripemd160.update(sha256_bpk)
        ripemd160_bpk = ripemd160.digest()

        hashed_pubkey_with_version = b'\x00' + ripemd160_bpk
        checksum = hashlib.sha256(hashlib.sha256(hashed_pubkey_with_version).digest()).digest()[:4]
        binary_address = hashed_pubkey_with_version + checksum
        bitcoin_address = base58.b58encode(binary_address).decode('utf-8')

        addresses.append((compressed_pubkey, bitcoin_address))
    return addresses