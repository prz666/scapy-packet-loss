# About

Ultra basic tool to measure uni-directional packet loss between two endpoints. 

`client.py` will send a stream of UDP packets at an adjustable rate, incrementing the IP ID field in the packet header for each packet, starting at 1. `server.py` will collect all received packets. Both will record the same source IP + IP ID to stdout. Then, it is a matter of diffing both log streams to assess the damage.

# Setup

See last steps in `lab_setup.sh`, which was used to test the solution in a sandbox using Linux network namespaces, along with using `tc` to simulate random percent-based packet drops.

# Caveats

Obviously, any firewalls or security groups etc. need to be open for any given flow.
