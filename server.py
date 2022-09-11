from scapy.all import sniff
from os import environ
from utils import debug_logging


def main():
    SCAPY_INTERFACE = environ.get("SCAPY_INTERFACE", "eth0")
    sniff(iface=SCAPY_INTERFACE, filter="udp port 6666", prn=debug_logging)


if __name__ == "__main__":
    main()
