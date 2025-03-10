# Name: Taaha Bin Mohsin

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

    if not all([number, as_ip, as_port]):
        return jsonify({"error": "Missing required parameters"}), 400

    fs_ip = get_ip_from_dns(hostname, as_ip, int(as_port))

    if not fs_ip:
        return jsonify({"error": "Could not resolve hostname"}), 400

    fs_url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"

    try:
        response = requests.get(fs_url, timeout=5)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        elif response.status_code == 400:
            return jsonify({"error": response.json().get("error", "Bad request to Fibonacci server")}), 400
        else:
            return jsonify({"error": "Fibonacci server error"}), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": "Failed to connect to Fibonacci server", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
