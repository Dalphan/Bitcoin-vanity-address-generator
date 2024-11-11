#!/usr/bin/env python3
# 2022/Dec/30, citb0in
import concurrent.futures
import os
import numpy as np
import fastecdsa.keys as fkeys
import fastecdsa.curve as fcurve
import secp256k1 as ice
import time

# how many cores to use
# num_cores = 1
num_cores = os.cpu_count()

# Set the number of addresses to generate
num_addresses = 500000

# Set the pattern
PATTERN = '1Dani'

# Define a worker function that generates a batch of addresses and returns them
def worker(start, end):
  # Generate a NumPy array of random private keys using fastecdsa
  private_keys = np.array([fkeys.gen_private_key(fcurve.P256) for _ in range(start, end)])

  # Use secp256k1 to convert the private keys to addresses
  thread_addresses = np.array([ice.privatekey_to_address(0, True, dec) for dec in private_keys])
  
  # Check if any address starts with the pattern
  for address in thread_addresses:
    if address.startswith(PATTERN):
      return thread_addresses, address

  return thread_addresses, None

found = False
tot_addresses = 0
# Use a ProcessPoolExecutor to generate the addresses in parallel
with concurrent.futures.ProcessPoolExecutor() as executor:
  while not found:
    start_time = time.time()
    
    # Divide the addresses evenly among the available CPU cores
    addresses_per_core = num_addresses // num_cores

    # Submit a task for each batch of addresses to the executor
    tasks = []
    for i in range(num_cores):
      start = i * addresses_per_core
      end = (i+1) * addresses_per_core
      tasks.append(executor.submit(worker, start, end))

    # Wait for the tasks to complete and retrieve the results
    tot_addresses += num_addresses
    for task in concurrent.futures.as_completed(tasks):
      address, match = task.result()
      if match:
        print(f'Found address: {match}')
        found = True
        break

    end_time = time.time()
    elapsed_time = end_time - start_time
    addresses_per_second = num_addresses / elapsed_time
    print(f'Generated {num_addresses} addresses in {elapsed_time:.2f} seconds ({addresses_per_second:.2f} addresses/second)')

# Write the addresses to a file
# np.savetxt('addresses_1M_with_singleCore.txt', addresses, fmt='%s')