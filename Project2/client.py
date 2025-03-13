import socket
import sys

def send_query(server, port, domain, identifier, flag):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server, port))
        message = f"0 {domain} {identifier} {flag}"
        s.send(message.encode())
        response = s.recv(1024).decode().strip()
        return response

def main(rs_host, port):
    with open("hostnames.txt", "r") as file:
        queries = file.readlines()

    identifier = 1
    for query in queries:
        parts = query.strip().split()
        domain, flag = parts[0], parts[1]

        response = send_query(rs_host, port, domain, identifier, flag)
        print(f"Query: {domain}, Response: {response}")
        identifier += 1

if __name__ == "__main__":
    rs_host = sys.argv[1]
    port = int(sys.argv[2])
    main(rs_host, port)
