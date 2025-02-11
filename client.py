import socket

def client():
    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[C]: Client socket created")
    except socket.error as err:
        print('socket open error: {} \n'.format(err))
        exit()

    # Connect to the server on localhost
    port = 50007
    localhost_addr = socket.gethostbyname(socket.gethostname())
    server_binding = (localhost_addr, port)

    cs.connect(server_binding)

    # Input string to send to the server
    message = input("[C]: Enter a string to send to the server: ")
    print(f"[C]: Sending to server: {message}")

    # Send the string to the server
    cs.send(message.encode('utf-8'))

    # Receive transformed string from the server
    data_from_server = cs.recv(1024).decode('utf-8')
    print(f"[C]: Received from server: {data_from_server}")

    # Close the client socket
    cs.close()

if __name__ == "__main__":
    client()
