from prometheus_client import start_http_server, Counter
from scapy.all import sniff, IP, UDP, Raw
from subprocess import check_output
from os import environ
from utils import debug_logging


c_flow_packets = Counter(
    "flow_packets", "Flow packets sent or received", ["src", "dst"]
)
c_lost_packets = Counter(
    "lost_packets", "Lost packets assuming no re-ordering", ["src", "dst"]
)

my_ifce, my_ip = check_output(
    "ip rou get 8.8.8.8 | grep dev | cut -d' ' -f5,7",
    shell=True,
).split()
my_ifce = my_ifce.decode()
my_ip = my_ip.decode()

SCAPY_SESSION_PORT = int(environ.get("SCAPY_SESSION_PORT", 26666))
SCAPY_METRICS_PORT = int(environ.get("SCAPY_METRICS_PORT", 8000))
SCAPY_SRC_NAME = environ.get("SCAPY_SRC_NAME", "A")
SCAPY_DST_NAME = environ.get("SCAPY_DST_NAME", "B")

last_id = 0


def packet_telemetry(pkt):
    c_flow_packets.labels(SCAPY_SRC_NAME, SCAPY_DST_NAME).inc()

    global last_id

    current_id = int(pkt[IP][UDP][Raw].load.decode())
    delta_id = current_id - last_id

    if delta_id > 1:
        c_lost_packets.labels(SCAPY_SRC_NAME, SCAPY_DST_NAME).inc(delta_id - 1)

    # only track monotonic progress
    if current_id > last_id:
        last_id = current_id

    debug_logging(pkt)


def main():
    bpf_filter = f"ip host {my_ip} and udp port {SCAPY_SESSION_PORT}"

    sniff(iface=my_ifce, filter=bpf_filter, prn=packet_telemetry)


if __name__ == "__main__":
    start_http_server(SCAPY_METRICS_PORT)
    main()
