import socket

def server():
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allows reusing the port immediately
        print("[S]: Server socket created")
    except socket.error as err:
        print('socket open error: {}\n'.format(err))
        exit()

    server_binding = ('', 50007)
    ss.bind(server_binding)
    ss.listen(1)

    print("[S]: Waiting for a connection...")
    csockid, addr = ss.accept()
    print("[S]: Got a connection request from a client at {}".format(addr))

    # Receive a string from the client
    data_from_client = csockid.recv(1024).decode('utf-8')
    print(f"[S]: Received from client: {data_from_client}")

    # Reverse the string and swap case
    transformed_data = data_from_client[::-1].swapcase()

    # Send the transformed string back to the client
    csockid.send(transformed_data.encode('utf-8'))

    # Close the sockets
    csockid.close()
    ss.close()

if __name__ == "__main__":
    server()
