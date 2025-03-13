import socket
import sys

def load_database(filename):
    db = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            db[parts[0].lower()] = parts[1]
    return db

def start_server(port, database):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(5)
    print(f"TLD Server listening on port {port}...")

    while True:
        client_socket, addr = server_socket.accept()
        data = client_socket.recv(1024).decode().strip()
        if not data:
            continue
        parts = data.split()
        domain, identifier = parts[1], parts[2]

        if domain in database:
            response = f"1 {domain} {database[domain]} {identifier} aa"
        else:
            response = f"1 {domain} 0.0.0.0 {identifier} nx"

        client_socket.send(response.encode())
        client_socket.close()

if __name__ == "__main__":
    port = int(sys.argv[1])
    database = load_database("ts1database.txt" if "ts1" in sys.argv[0] else "ts2database.txt")
    start_server(port, database)
