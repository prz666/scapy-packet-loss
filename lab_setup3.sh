#!/usr/bin/bash

# download latest prometheus
apt update
wget https://github.com/prometheus/prometheus/releases/download/v2.38.0/prometheus-2.38.0.linux-arm64.tar.gz
tar -xzvf prometheus-2.38.0.linux-arm64.tar.gz
rm prometheus-2.38.0.linux-arm64.tar.gz

# clone repo
git clone https://github.com/prz666/scapy-packet-loss.git

# setup python virtual environment
cd scapy-packet-loss
sudo apt install python3.10-venv
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
deactivate

# generate prometheus config file
cat <<EOT > /tmp/prometheus.yml
global:
  scrape_interval: 1m
  evaluation_interval: 1m

scrape_configs:
  - job_name: "scapy"
    static_configs:
      - targets: ["127.0.0.1:8001"]
      - targets: ["127.0.0.1:8002"]
EOT

# login to either client or server and start tmux session
tmux

# pane 1: start prometheus
cd /root/prometheus-2.38.0.linux-arm64
./prometheus --config.file="/tmp/prometheus.yml"

# pane 2: launch server first
sudo su -
cd /home/ubuntu/scapy-packet-loss
source venv/bin/activate
export SCAPY_SRC_NAME=obkio1
export SCAPY_DST_NAME=obkio2
export SCAPY_SESSION_PORT=26661
export SCAPY_METRICS_PORT=8001
python server.py

# pane 3: then client
sudo su -
cd /home/ubuntu/scapy-packet-loss
source venv/bin/activate
export SCAPY_TARGET_IP=x.x.x.x
export SCAPY_SEND_PPS=10
export SCAPY_SEND_TOTAL=100000
export SCAPY_SRC_NAME=obkio1
export SCAPY_DST_NAME=obkio2
export SCAPY_SESSION_PORT=26661
export SCAPY_METRICS_PORT=8001
python client.py
