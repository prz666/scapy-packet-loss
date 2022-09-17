from prometheus_client import start_http_server, Counter
from scapy.all import sniff, IP
from os import environ
from utils import debug_logging


c_flow_packets = Counter(
    "flow_packets", "Flow packets sent or received", ["src", "dst"]
)
c_lost_packets = Counter(
    "lost_packets", "Lost packets assuming no re-ordering", ["src", "dst"]
)

last_id = 0


def packet_telemetry(pkt):
    c_flow_packets.labels("A", "B").inc()

    global last_id

    current_id = pkt[IP].id
    delta_id = current_id - last_id

    if delta_id > 1:
        c_lost_packets.labels("A", "B").inc(delta_id - 1)

    last_id = current_id

    debug_logging(pkt)


def main():
    SCAPY_INTERFACE = environ.get("SCAPY_INTERFACE", "eth0")
    sniff(iface=SCAPY_INTERFACE, filter="udp port 6666", prn=packet_telemetry)


if __name__ == "__main__":
    start_http_server(8000)
    main()
