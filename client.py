from scapy.all import send, IP, UDP
from os import environ
from time import sleep
from utils import debug_logging


def main():
    SCAPY_TARGET_IP = environ.get("SCAPY_TARGET_IP")
    SCAPY_SEND_INTERVAL = float(environ.get("SCAPY_SEND_INTERVAL", 1))
    SCAPY_SEND_PKT_COUNT = int(environ.get("SCAPY_SEND_PKT_COUNT", 100))

    id = 1
    while True:
        id %= 2**16
        pkt = IP(dst=SCAPY_TARGET_IP, id=id) / UDP(sport=6666, dport=6666)

        debug_logging(pkt)
        send(pkt, verbose=False)

        id += 1
        if id > SCAPY_SEND_PKT_COUNT:
            break

        sleep(SCAPY_SEND_INTERVAL)


if __name__ == "__main__":
    main()
