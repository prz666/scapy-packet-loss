from prometheus_client import start_http_server, Gauge, Counter
from scapy.all import send, IP, UDP
from os import environ
from time import sleep
from utils import debug_logging


SCAPY_TARGET_IP = environ.get("SCAPY_TARGET_IP")
SCAPY_SESSION_PORT = int(environ.get("SCAPY_SESSION_PORT", 26666))
SCAPY_METRICS_PORT = int(environ.get("SCAPY_METRICS_PORT", 8000))
SCAPY_SEND_PPS = int(environ.get("SCAPY_SEND_PPS", 1))
SCAPY_SEND_TOTAL = int(environ.get("SCAPY_SEND_TOTAL", 0))
SCAPY_TEST_SIGNAL = environ.get("SCAPY_TEST_SIGNAL")
SCAPY_SRC_NAME = environ.get("SCAPY_SRC_NAME", "A")
SCAPY_DST_NAME = environ.get("SCAPY_DST_NAME", "B")


def main():
    g_flow_rate_pps = Gauge(
        "flow_rate_pps", "Flow (src -> dst) packet rate per second", ["src", "dst"]
    )
    g_flow_rate_pps.labels(SCAPY_SRC_NAME, SCAPY_DST_NAME).set(SCAPY_SEND_PPS)

    c_flow_packets = Counter(
        "flow_packets", "Flow packets sent or received", ["src", "dst"]
    )

    if SCAPY_TEST_SIGNAL:
        for long_id in SCAPY_TEST_SIGNAL.split():
            short_id = long_id % (2 << 15)
            pkt = (
                IP(dst=SCAPY_TARGET_IP, id=short_id)
                / UDP(sport=SCAPY_SESSION_PORT, dport=SCAPY_SESSION_PORT)
                / long_id
            )

            debug_logging(pkt)
            send(pkt, verbose=False)
            c_flow_packets.labels(SCAPY_SRC_NAME, SCAPY_DST_NAME).inc()

            sleep(1.0 / SCAPY_SEND_PPS)

        # to let prometheus scrape client metrics
        sleep(100000)

    else:
        long_id = 1
        while True:
            short_id = long_id % (2 << 15)
            pkt = (
                IP(dst=SCAPY_TARGET_IP, id=short_id)
                / UDP(sport=SCAPY_SESSION_PORT, dport=SCAPY_SESSION_PORT)
                / str(long_id)
            )

            debug_logging(pkt)
            send(pkt, verbose=False)
            c_flow_packets.labels(SCAPY_SRC_NAME, SCAPY_DST_NAME).inc()

            long_id += 1
            if SCAPY_SEND_TOTAL > 0:
                if long_id > SCAPY_SEND_TOTAL:
                    break

            sleep(1.0 / SCAPY_SEND_PPS)


if __name__ == "__main__":
    start_http_server(SCAPY_METRICS_PORT)
    main()
