import socket
import hashlib
import json

# Configure pool connection details
pool_host = "public-pool.io"
pool_port = 21496
username = "bc1qwp44lvxgrhh42de507kezjspcyh8cvw6tvuykp"
password = "x"

# Create a TCP socket and connect to the pool
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((pool_host, pool_port))

# Start mining loop
while True:
    try:
        # Send mining subscription request
        subscribe_request = json.dumps({"id": 1, "method": "mining.subscribe", "params": []}) + "\n"
        conn.sendall(subscribe_request.encode())

        # Receive subscription response
        subscribe_response = ""
        while not subscribe_response.endswith("\n"):
            data = conn.recv(4096).decode()
            if not data:
                break
            subscribe_response += data

        # Parse valid JSON response from the received data
        valid_subscribe_response = subscribe_response[:subscribe_response.index("\n") + 1]
        subscribe_data = json.loads(valid_subscribe_response)

        # Extract subscription details
        subscription_id = subscribe_data["result"][0]

        # Send authorization request
        authorize_request = json.dumps({"id": 2, "method": "mining.authorize", "params": [username, password]}) + "\n"
        conn.sendall(authorize_request.encode())

        # Receive authorization response
        authorize_response = ""
        while not authorize_response.endswith("\n"):
            data = conn.recv(4096).decode()
            if not data:
                break
            authorize_response += data

        # Parse valid JSON response from the received data
        valid_authorize_response = authorize_response[:authorize_response.index("\n") + 1]
        authorize_data = json.loads(valid_authorize_response)

        if "result" in authorize_data and authorize_data["result"]:
            # Fetch mining job
            getwork_request = json.dumps({"id": 3, "method": "mining.get_work", "params": [subscription_id]}) + "\n"
            conn.sendall(getwork_request.encode())

            # Receive mining job response
            getwork_response = ""
            while not getwork_response.endswith("\n"):
                data = conn.recv(4096).decode()
                if not data:
                    break
                getwork_response += data

            # Parse valid JSON response from the received data
            valid_getwork_response = getwork_response[:getwork_response.index("\n") + 1]
            getwork_data = json.loads(valid_getwork_response)

            if "result" in getwork_data and getwork_data["result"] is not None:
                # Extract job details
                job = getwork_data["result"]
                data = job["data"]
                target = job["target"]

                # Perform mining calculations
                nonce = 0
                while nonce < 2**32:  # Nonce is 32-bit in Getwork protocol
                    header = data + format(nonce, '08x')
                    hash_result = hashlib.sha256(hashlib.sha256(header.encode()).digest()).hexdigest()

                    # Check if a valid hash is found
                    if hash_result <= target:
                        print("Valid hash found!")
                        print("Nonce:", nonce)
                        print("Hash result:", hash_result)
                        break

                    nonce += 1

    except Exception as e:
        print("Error:", e)
