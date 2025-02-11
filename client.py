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

    # Open the input file and send each line to the server
    with open("in-proj.txt", "r") as input_file:
        for line in input_file:
            message = line.strip()  # Remove leading/trailing whitespace
            if message:  # Send only non-empty lines
                print(f"[C]: Sending to server: {message}")
                cs.send(message.encode('utf-8'))

                # Receive transformed response from server
                data_from_server = cs.recv(200).decode('utf-8')
                print(f"[C]: Received from server: {data_from_server}")

    # Close the client socket
    cs.close()

if __name__ == "__main__":
    client()
