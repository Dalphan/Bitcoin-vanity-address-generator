from fastecdsa import keys, curve
import hashlib
from Crypto.Hash import RIPEMD160  # Import RIPEMD-160 from pycryptodome
import base58
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import coincurve

NUM_THREADS = 8

def generate_address2():
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
    
    return compressed_pubkey, bitcoin_address

def generate_address():
    # Step 1: Generate private key
    private_key = keys.gen_private_key(curve.secp256k1)

    # Step 2: Generate public key from private key
    public_key = keys.get_public_key(private_key, curve.secp256k1)

    # Step 3: Convert public key to compressed format
    compressed_prefix = '02' if public_key.y % 2 == 0 else '03'
    compressed_pubkey = compressed_prefix + f'{public_key.x:064x}'

    # Step 4: Generate Bitcoin address
    # Perform SHA-256 hashing on the compressed public key
    sha256_bpk = hashlib.sha256(bytes.fromhex(compressed_pubkey)).digest()

    # Perform RIPEMD-160 hashing on the SHA-256 result
    ripemd160 = RIPEMD160.new()
    ripemd160.update(sha256_bpk)
    ripemd160_bpk = ripemd160.digest()

    # Add version byte (0x00 for Main Network)
    hashed_pubkey_with_version = b'\x00' + ripemd160_bpk

    # Perform SHA-256 hash twice on the extended RIPEMD-160 result
    checksum = hashlib.sha256(hashlib.sha256(hashed_pubkey_with_version).digest()).digest()[:4]

    # Add the checksum to the extended RIPEMD-160 hash
    binary_address = hashed_pubkey_with_version + checksum

    # Finally, convert the binary address to Base58
    bitcoin_address = base58.b58encode(binary_address).decode('utf-8')

    # print("Private Key:", f'{private_key:064x}')
    # print("Compressed Public Key:", compressed_pubkey)
    # print("Bitcoin Address:", bitcoin_address)
    return compressed_pubkey, bitcoin_address
    
def main():
    num_generated = 0
    start_time = time.time()
    pattern = '1Dan'

    with ProcessPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        while True:
            futures.append(executor.submit(generate_address2))
            if len(futures) >= 1000:
                for future in as_completed(futures):
                    pub_key, bitcoin_address = future.result()
                    num_generated += 1
                    if pattern in bitcoin_address[:pattern.__len__()]:
                        print(f"Address:\t {bitcoin_address}")
                        print(f"Public Key:\t {pub_key}")
                        executor.shutdown(wait=False)
                        return
                futures = []
            
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                print(f"Addresses generated per second: {num_generated / elapsed_time:.2f}")
                start_time = time.time()
                num_generated = 0
    
if __name__ == "__main__":
    main()
