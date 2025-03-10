import socket

def server():
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allows immediate reuse of port
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

    # Open the output file for writing the transformed lines
    with open("out-proj.txt", "w") as output_file:
        while True:
            # Receive a line from the client
            data_from_client = csockid.recv(200).decode('utf-8').strip()
            
            if not data_from_client:  # Stop if client sends an empty string (EOF)
                break
            
            print(f"[S]: Received from client: {data_from_client}")

            # Reverse the string and swap case
            transformed_data = data_from_client[::-1].swapcase()

            # Write the transformed line to the output file
            output_file.write(transformed_data + "\n")

            # Send the transformed string back to the client for verification (optional)
            csockid.send(transformed_data.encode('utf-8'))

    # Close the sockets
    csockid.close()
    ss.close()
    print("[S]: Output saved to out-proj.txt")

if __name__ == "__main__":
    server()
