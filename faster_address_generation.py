import hashlib
from Crypto.Hash import RIPEMD160
import base58
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import coincurve
import os

NUM_THREADS = os.cpu_count() or 8  # Utilize all available CPU cores

PATTERN = 'Dani'

def generate_addresses(batch_size=1000):
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

def main():
    num_generated = 0
    start_time = time.time()

    with ProcessPoolExecutor(max_workers=NUM_THREADS) as executor:
        # Submit initial batch tasks
        future_to_batch = {executor.submit(generate_addresses, 1000): i for i in range(NUM_THREADS)}

        while future_to_batch:
            # As each batch completes
            done, _ = as_completed(future_to_batch), None
            for future in done:
                batch_addresses = future.result()
                batch_index = future_to_batch.pop(future)

                for pub_key, bitcoin_address in batch_addresses:
                    num_generated += 1
                    # Check for the pattern "Dan" after the first '1'
                    if '1' in bitcoin_address:
                        if bitcoin_address[1:1 + len(PATTERN)] == PATTERN:
                            print(f"Found address with pattern '{PATTERN}': {bitcoin_address}")
                            print(f"Compressed Public Key: {pub_key}")
                            executor.shutdown(wait=False)
                            return

                # Logging the generation rate every second
                elapsed_time = time.time() - start_time
                if elapsed_time >= 1:
                    print(f"Addresses generated per second: {num_generated / elapsed_time:.2f}")
                    start_time = time.time()
                    num_generated = 0

                # Submit a new batch task
                future_to_batch[executor.submit(generate_addresses, 1000)] = batch_index

if __name__ == "__main__":
    main()