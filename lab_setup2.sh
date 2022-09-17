#!/usr/bin/bash

# on WSL2

# different setup with bridge on host and Prometheus server scraping metrics
ip link add name br0 type bridge
ip addr add dev br0 192.168.0.254/24


ip netns add ns1
ip link add name veth1 type veth peer name vethX
ip link set vethX netns ns1
ip netns exec ns1 ip link set vethX name eth0
ip netns exec ns1 ip link set lo up
ip netns exec ns1 ip link set eth0 up
ip link set veth1 master br0
ip link set veth1 up
ip netns exec ns1 ip addr add dev eth0 192.168.0.1/24


ip netns add ns2
ip link add name veth2 type veth peer name vethX
ip link set vethX netns ns2
ip netns exec ns2 ip link set vethX name eth0
ip netns exec ns2 ip link set lo up
ip netns exec ns2 ip link set eth0 up
ip link set veth2 master br0
ip link set veth2 up
ip netns exec ns2 ip addr add dev eth0 192.168.0.2/24

ip link set br0 up

# intdoduce 10% loss from ns1 to ns2 (ie, egress towards ns2, from bridge perspective)
tc qdisc add dev veth2 root netem loss 10%

# launch server first
ip netns exec ns2 python server.py | tee /tmp/rx

# then client
export SCAPY_TARGET_IP=192.168.0.2
export SCAPY_SEND_PPS=10
export SCAPY_SEND_TOTAL=100000
ip netns exec ns1 python client.py | tee /tmp/tx

# diff results
wc -l /tmp/tx /tmp/rx
colordiff -y /tmp/tx /tmp/rx

# prometheus server
cat <<EOT > /tmp/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "scapy"
    static_configs:
      - targets: ["192.168.0.1:8000"]
      - targets: ["192.168.0.2:8000"]
EOT

# start the server
prometheus --config.file="/tmp/prometheus.yml"
