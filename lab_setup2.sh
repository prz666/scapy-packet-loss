#!/usr/bin/bash

# NOTE1: run as root

# NOTE2: does not work unde WSL2 (missing support for netem)

# download latest prometheus
apt update
wget https://github.com/prometheus/prometheus/releases/download/v2.38.0/prometheus-2.38.0.linux-arm64.tar.gz
tar -xzvf prometheus-2.38.0.linux-arm64.tar.gz
rm prometheus-2.38.0.linux-arm64.tar.gz

# clone repo
git clone https://github.com/prz666/scapy-packet-loss.git

# setup python virtual environment
cd scapy-packet-loss
apt install python3.10-venv
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
deactivate

# generate prometheus config file
cat <<EOT > /tmp/prometheus.yml
global:
  scrape_interval: 10s
  evaluation_interval: 10s

scrape_configs:
  - job_name: "scapy"
    static_configs:
      - targets: ["192.168.0.1:8000"]
      - targets: ["192.168.0.2:8000"]
EOT

# network plumbing using linux network namespaces only
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

# start prometheus
cd /root/prometheus-2.38.0.linux-arm64
./prometheus --config.file="/tmp/prometheus.yml"

# launch server first
cd /root/scapy-packet-loss
source venv/bin/activate
ip netns exec ns2 python server.py | tee /tmp/rx

# then client
cd /root/scapy-packet-loss
source venv/bin/activate
export SCAPY_TARGET_IP=192.168.0.2
export SCAPY_SEND_PPS=10
export SCAPY_SEND_TOTAL=100000
export SCAPY_TEST_SIGNAL=""
ip netns exec ns1 python client.py | tee /tmp/tx

# intdoduce 10% loss from ns1 to ns2 (ie, egress towards ns2, from bridge perspective)
tc qdisc add dev veth2 root netem loss 10%

# diff results
wc -l /tmp/tx /tmp/rx
colordiff -y /tmp/tx /tmp/rx
