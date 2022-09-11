import sys
from os import environ
from datetime import datetime
from scapy.all import IP


SCAPY_LOG_WITH_TIMESTAMP = environ.get("SCAPY_LOG_WITH_TIMESTAMP", False)


def debug_logging(pkt):
    if SCAPY_LOG_WITH_TIMESTAMP:
        now = datetime.now()
        t = now.strftime("%H:%M:%S")
        print(f"{t} {pkt[IP].src} {pkt.id}")
    else:
        print(f"{pkt[IP].src} {pkt.id}")

    sys.stdout.flush()
