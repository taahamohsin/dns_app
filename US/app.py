from flask import Flask, request, jsonify
import requests
import socket

app = Flask(__name__)

def get_ip_from_dns(hostname, as_ip, as_port):
    dns_query = f"TYPE=A\nNAME={hostname}\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    try:
        sock.sendto(dns_query.encode(), (as_ip, int(as_port)))
        response, _ = sock.recvfrom(1024)
        response_lines = response.decode().split('\n')
        response_dict = {}
        for line in response_lines:
            if line:
                key, value = line.split('=')
                response_dict[key] = value
        return response_dict.get('VALUE')
    except socket.timeout:
        return None
    finally:
        sock.close()

@app.route('/fibonacci', methods=['GET'])
def fibonacci_request():
    hostname = request.args.get('hostname', 'fibonacci.com')
    fs_port = request.args.get('fs_port', '9090')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip', 'localhost')
    as_port = request.args.get('as_port', '53533')

    print(f"🔹 Querying AS {as_ip}:{as_port} for hostname {hostname}")

    if not all([number, as_ip, as_port]):
        return jsonify({"error": "Missing required parameters"}), 400

    fs_ip = get_ip_from_dns(hostname, as_ip, int(as_port))
    print(f"🔹 AS Response - Resolved IP: {fs_ip}")

    if not fs_ip:
        return jsonify({"error": "Could not resolve hostname"}), 400

    fs_url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"
    print(f"🔹 Sending request to FS: {fs_url}")

    try:
        response = requests.get(fs_url, timeout=5)
        response.raise_for_status()
        return jsonify({"result": response.text}), 200
    except requests.RequestException as e:
        return jsonify({"error": "Failed to connect to Fibonacci server", "details": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
