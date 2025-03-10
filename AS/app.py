# Name: Taaha Bin Mohsin

import socket
import os

DNS_FILE = "dns_records.txt"

if not os.path.exists(DNS_FILE):
    with open(DNS_FILE, "w") as f:
        pass
try:
    with open(DNS_FILE, "r") as f:
        dns_records = dict(line.strip().split(maxsplit=1) for line in f if line.strip())
except FileNotFoundError:
    dns_records = {}

def save_dns_records():
    with open(DNS_FILE, "w") as f:
        for hostname, ip in dns_records.items():
            f.write(f"{hostname} {ip}\n")

UDP_IP = "0.0.0.0"
UDP_PORT = 53533
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("0.0.0.0", 53533))

print(f"Authoritative DNS Server listening on UDP {UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    message = data.decode().strip()

    print(f"Received message from {addr}: {message}")

    params = dict(item.split("=", 1) for item in message.split("\n") if "=" in item)
    print(f"Parsed params: {params}")

    if "NAME" in params and "VALUE" in params and "TYPE" in params and params["TYPE"] == "A":
        hostname = params["NAME"]
        ip_address = params["VALUE"]
        ttl = params.get("TTL", "10")
        print(f"Registering: {hostname} -> {ip_address}")

        dns_records[hostname] = ip_address
        save_dns_records()
        print("Saved DNS records")

    elif "TYPE" in params and params["TYPE"] == "A" and "NAME" in params:
        hostname = params["NAME"]

        if hostname in dns_records:
            response = f"TYPE=A\nNAME={hostname}\nVALUE={dns_records[hostname]}\nTTL=10"
        else:
            response = "ERROR=Hostname not found"

        sock.sendto(response.encode(), addr)

    else:
        response = "ERROR=Invalid request format"
        sock.sendto(response.encode(), addr)
