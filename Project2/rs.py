import socket
import sys

def load_database(filename):
    db = {}
    with open(filename, 'r') as file:
        lines = file.readlines()
        ts1_host = lines[0].strip().split()[1]
        ts2_host = lines[1].strip().split()[1]
        for line in lines[2:]:
            parts = line.strip().split()
            db[parts[0].lower()] = parts[1]
    return db, ts1_host, ts2_host

def start_server(port, database, ts1_host, ts2_host):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(5)
    print(f"Root DNS server listening on port {port}...")

    while True:
        client_socket, addr = server_socket.accept()
        data = client_socket.recv(1024).decode().strip()
        if not data:
            continue
        parts = data.split()
        domain, identifier, flag = parts[1], parts[2], parts[3]

        if domain in database:
            response = f"1 {domain} {database[domain]} {identifier} aa"
        elif domain.endswith(".com"):
            response = f"1 {domain} {ts1_host} {identifier} ns"
        elif domain.endswith(".edu"):
            response = f"1 {domain} {ts2_host} {identifier} ns"
        else:
            response = f"1 {domain} 0.0.0.0 {identifier} nx"

        client_socket.send(response.encode())
        client_socket.close()

if __name__ == "__main__":
    port = int(sys.argv[1])
    database, ts1_host, ts2_host = load_database("rsdatabase.txt")
    start_server(port, database, ts1_host, ts2_host)
