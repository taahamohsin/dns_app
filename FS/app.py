# Name: Taaha Bin Mohsin

from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

def fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

def register_with_as(hostname, ip, as_ip, as_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10)
        message = f"TYPE=A\nNAME={hostname}\nVALUE={ip}\nTTL=10".encode()
        sock.sendto(message, (as_ip, int(as_port)))
        return "Success"
    except socket.timeout:
        return "ERROR=Timeout while registering"
    except Exception as e:
        return f"ERROR={str(e)}"
    finally:
        sock.close()

@app.route('/register', methods=['PUT'])
def register():
    try:
        data = request.get_json()
        hostname = data["hostname"]
        fs_ip = socket.gethostbyname(socket.gethostname())
        ip = data.get("ip", fs_ip)
        as_ip = data["as_ip"]
        as_port = data["as_port"]
        print(f"Attempting to register with AS at {as_ip}:{as_port}")

        if not all([hostname, ip, as_ip, as_port]):
            return jsonify({"error": "Missing required parameters"}), 400

        response = register_with_as(hostname, ip, as_ip, as_port)

        if "ERROR" in response:
            return jsonify({"error": response}), 500

        return jsonify({"message": "Registration successful"}), 201
    except (KeyError, TypeError):
        return jsonify({"error": "Invalid JSON format"}), 400

@app.route('/fibonacci', methods=['GET'])
def compute_fibonacci():
    number = request.args.get("number")

    if not number or not number.isdigit() or int(number) < 0:
        return jsonify({"error": "Invalid number"}), 400

    number = int(number)
    result = fibonacci(number)

    return jsonify({"fibonacci": result}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
