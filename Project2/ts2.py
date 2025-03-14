import re
import socket
import sys

NO_IP = "0.0.0.0"

#-----code to lookup the ip address via the Domain name------
def lookup_ip(domain_name):
    print("searching for " + domain_name)
    #search for the exact name
    for x in range(len(dns_names)):
        if(dns_names[x] == domain_name):
            return values[x], "aa"
    return NO_IP, "nx"

#----------write the response string---------------------    

def write_response(domain_name, result, flag, req_id):
    return "1 " + domain_name + " " + result + " " + str(req_id) + " " + flag

#----------create the response ------------------------
def get_response(request):
    result = ""
    req_parts = request.split(" ")
    if(len(req_parts) != 4):
        return "ERROR: Invalid Request, DNS lookup must be of format '0 <DOMAIN_NAME> <REQUEST_ID> <FLAG>'"
    if(req_parts[0] != "0"):
        return "ERROR: Invalid Request, DNS lookup must start with 0"
    domain_name = req_parts[1]
    req_id = 0
    try:
        req_id = int(req_parts[2])
    except ValueError:
        return "ERROR: Invalid Request, DNS lookup request ID must be numeric"
    flag =  req_parts[3]   
    if( flag != "it" and flag != "rd"):
        return "ERROR: Invalid Request, DNS lookup flags must be either 'it' or 'rd'"

    result, flag = lookup_ip(domain_name)
    return write_response(domain_name, result, flag, req_id)

#----------run the server ------------------------
def server(server_port):
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("[S]: Server socket created")
    except socket.error as err:
        print(f'Socket open error: {err}\n')
        exit()

    server_binding = ('', server_port)
    serverSocket.bind(server_binding)
    serverSocket.listen(5)

    print("[S]: Server is waiting for a connection...")

    with open("ts2responses.txt", "w") as output_file:
        while True:
            connectionSocket, addr = serverSocket.accept()
            print(f"[S]: Client is connected at {addr}")
            data = connectionSocket.recv(200).decode('utf-8')
            if not data:
                print("No Data received")  
            else:
                modifiedData = get_response(data.strip())
                print(f"[S]: Received: {data} | Modified: {modifiedData}")
                output_file.write(modifiedData + '\n')
                output_file.flush() 
                connectionSocket.sendall(modifiedData.encode('utf-8'))
            connectionSocket.close()
    serverSocket.close()

#-------code to read from space separted file--------------
def populate_list_from_file(file_name):
    dns_names, values = [], []
    
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.split()
                if len(parts) == 2: 
                    dns_names.append(parts[0])
                    values.append(parts[1])
                else:
                    print(f"Error: Invalid line: {line.strip()}")
        
        return dns_names, values
    except FileNotFoundError:
        print(f"Error: The file: '{file_name}' is not found.")
        dns_names, values
    except Exception as e:
        print(f"Error: Unable to read database file:{file_name} {e}")
        dns_names, values
#----------------------main_program --------------------------
server_port = 0
if len(sys.argv) != 2:
    print("Error: Missing Argument <port>")
    sys.exit(1)
else:
    try:
       server_port = int(sys.argv[1])
    except Exception:
        print(f"Error: Invalid port:{sys.argv[1]}")
        sys.exit(1) 

file_name = "ts2database.txt"
dns_names, values = populate_list_from_file(file_name)


if __name__ == "__main__":
    server(server_port)