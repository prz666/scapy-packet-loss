from scapy.all import sniff, IP
from os import environ
import sys


def debug_logging(pkt):
    print(f"{pkt[IP].src} {pkt.id}")
    sys.stdout.flush()


def main():
    SCAPY_INTERFACE = environ.get("SCAPY_INTERFACE", "eth0")
    sniff(iface=SCAPY_INTERFACE, filter="udp port 6666", prn=debug_logging)


if __name__ == "__main__":
    main()
