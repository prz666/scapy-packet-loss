from prometheus_client import start_http_server, Gauge, Counter
from scapy.all import send, IP, UDP
from os import environ
from time import sleep
from utils import debug_logging


def main():
    SCAPY_TARGET_IP = environ.get("SCAPY_TARGET_IP")
    SCAPY_SEND_PPS = int(environ.get("SCAPY_SEND_PPS", 1))
    SCAPY_SEND_TOTAL = int(environ.get("SCAPY_SEND_TOTAL", 100))

    g_flow_rate_pps = Gauge(
        "flow_rate_pps", "Flow (A->B) packet rate per second", ["src", "dst"]
    )
    g_flow_rate_pps.labels("A", "B").set(SCAPY_SEND_PPS)

    c_flow_packets = Counter(
        "flow_packets", "Flow packets sent or received", ["src", "dst"]
    )

    current_id = 1

    while True:
        current_id %= 2**16
        pkt = IP(dst=SCAPY_TARGET_IP, id=current_id) / UDP(sport=6666, dport=6666)

        debug_logging(pkt)
        send(pkt, verbose=False)
        c_flow_packets.labels("A", "B").inc()

        current_id += 1
        if current_id > SCAPY_SEND_TOTAL:
            break

        sleep(1.0 / SCAPY_SEND_PPS)


if __name__ == "__main__":
    start_http_server(8000)
    main()
