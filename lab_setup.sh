#!/usr/bin/bash

# on Ubuntu 22.04
apt install -y colordiff python3.10-venv

# setup network namespaces and veth link between the two
ip netns add ns1
ip netns add ns2
ip link add name veth1 type veth peer name veth2
ip link set veth1 netns ns1
ip link set veth2 netns ns2
ip netns exec ns1 ip link set veth1 name eth0
ip netns exec ns2 ip link set veth2 name eth0
ip netns exec ns1 ip link set lo up
ip netns exec ns2 ip link set lo up
ip netns exec ns1 ip link set eth0 up
ip netns exec ns2 ip link set eth0 up
ip netns exec ns1 ip addr add dev eth0 192.168.0.1/30
ip netns exec ns2 ip addr add dev eth0 192.168.0.2/30

# intdoduce 10% loss (on sending side, because qdisc applied in egress)
ip netns exec ns1 tc qdisc add dev eth0 root netem loss 10%

# launch server first
ip netns exec ns2 python server.py | tee /tmp/rx

# then client
export SCAPY_TARGET_IP=192.168.0.2
export SCAPY_SEND_INTERVAL=0.1
export SCAPY_SEND_PKT_COUNT=200
ip netns exec ns1 python client.py | tee /tmp/tx

# diff results
wc -l /tmp/tx /tmp/rx
colordiff -y /tmp/tx /tmp/rx
