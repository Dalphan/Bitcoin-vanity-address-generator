import hashlib
from Crypto.Hash import RIPEMD160  # Import RIPEMD-160 from pycryptodome
import base58
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import coincurve

def generate_address():
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
    
def main(pattern, num_threads):
    num_generated = 0
    start_time = time.time()
    total_time = start_time
    total_addresses = 0
    with ProcessPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        while True:
            futures.append(executor.submit(generate_address))
            if len(futures) >= 1000:
                for future in as_completed(futures):
                    pub_key, bitcoin_address = future.result()
                    num_generated += 1
                    if pattern in bitcoin_address[:pattern.__len__()]:
                        print(f"- Address: {bitcoin_address}")
                        print(f"- Public Key: {pub_key}")

                        total_time = time.time() - total_time
                        print(f"- Total time taken: {total_time:.2f} seconds")
                        total_addresses += num_generated
                        print(f"- Total addresses generated: {total_addresses}")
                        executor.shutdown(wait=False)
                        return
                futures = []
            
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                print(f"Addresses generated per second: {num_generated / elapsed_time:.2f}")
                start_time = time.time()
                total_addresses += num_generated
                num_generated = 0
    
# if __name__ == "__main__":
#     main("Dan", os.cpu_count())
