import sys
from os import environ
from datetime import datetime
from scapy.all import IP, UDP, Raw


SCAPY_LOG_WITH_TIMESTAMP = environ.get("SCAPY_LOG_WITH_TIMESTAMP", False)


def debug_logging(pkt):
    if SCAPY_LOG_WITH_TIMESTAMP:
        now = datetime.now()
        t = now.strftime("%H:%M:%S")
        pkt_src_ip = pkt[IP].src
        pkt_id = pkt[IP][UDP][Raw].load.decode()
        print(f"{t} {pkt_src_ip} {pkt_id}")
    else:
        print(f"{pkt_src_ip} {pkt_id}")

    sys.stdout.flush()
