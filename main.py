import argparse
import os
from address_generation import main as v1
from faster_address_generation import main as v2
from fastest_address_generation import main as v3

def main():
    NUM_THREADS = os.cpu_count()

    parser = argparse.ArgumentParser(description='Bitcoin Vanity Address Generator')
    parser.add_argument('-p', '--prefix', type=str, help='The prefix for the vanity address', required=True)
    parser.add_argument('-v', '--version', type=int, help='The generator to use: '+
                        '1 for address_generation.py, ' +
                        '2 for faster_address_generation.py, ' +
                        '3 for fastest_address_generation_.py', default=3)
    parser.add_argument('-t', '--threads', type=int, help='The number of addresses to generate', default=NUM_THREADS)
    args = parser.parse_args()

    print(f"Generating Bitcoin address(es) with prefix: {args.prefix}" + (f" using {args.threads} threads" if args.threads > 1 else ""))
    
    if args.version == 1:
        v1(args.prefix, args.threads)
    elif args.version == 2:
        v2(args.prefix, args.threads)
    elif args.version == 3:
        v3(args.prefix, args.threads)
    else:
        print("Invalid version specified. Exiting...")
        exit(1)

if __name__ == '__main__':
    main()