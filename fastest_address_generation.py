import address_gen  # Import the compiled Cython module
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import os

NUM_THREADS = os.cpu_count() or 10
PATTERN = 'Danie'

def main():
    num_generated = 0
    start_time = time.time()
    total_time = start_time
    total_addresses = 0
    with ProcessPoolExecutor(max_workers=NUM_THREADS) as executor:
        future_to_batch = {executor.submit(address_gen.generate_addresses_cython, 1000): i for i in range(NUM_THREADS)}

        while future_to_batch:
            done, _ = as_completed(future_to_batch), None
            for future in done:
                batch_addresses = future.result()
                batch_index = future_to_batch.pop(future)

                for pub_key, bitcoin_address in batch_addresses:
                    num_generated += 1
                    if bitcoin_address[1:1 + len(PATTERN)] == PATTERN:
                        print(f"Address: {bitcoin_address}")
                        print(f"Public Key: {pub_key}")
                        
                        total_time = time.time() - total_time
                        print(f"Total time taken: {total_time:.2f} seconds")
                        total_addresses += num_generated
                        print(f"Total addresses generated: {total_addresses}")
                        executor.shutdown(wait=False)
                        return

                elapsed_time = time.time() - start_time
                if elapsed_time >= 1:
                    print(f"Addresses generated per second: {num_generated / elapsed_time:.2f}")
                    start_time = time.time()
                    total_addresses += num_generated
                    num_generated = 0

                # Submit a new batch task
                future_to_batch[executor.submit(address_gen.generate_addresses_cython, 1000)] = batch_index
    


if __name__ == "__main__":
    main()