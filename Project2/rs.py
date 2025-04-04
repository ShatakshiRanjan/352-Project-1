import re
import socket
import sys

NO_IP = "0.0.0.0"

#---- send message via client -------------------------------

def send_message(dns_host, port, domain_name, req_id, flag):
    print(f"connecting to client{dns_host}:{port}")
    response = write_response(domain_name, NO_IP, "nx", req_id)
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((dns_host, port))
        request = write_request(domain_name, flag, req_id)
        client_socket.sendall(request.encode(), )
        response = client_socket.recv(200).decode()
        print(f"Received message:{response}")
        client_socket.close()
    except Exception as e:
        print(f"Exception while connecting to host:{dns_host}:{port}")
        print(f"Error: {e}")
    return response

#-----code to lookup the ip address via the Domain name------
def lookup_ip(domain_name):
    print("searching for " + domain_name)
    #search for the exact name
    for x in range(len(dns_names)):
        if(dns_names[x] == domain_name):
            return values[x], "aa"
    return NO_IP, "nx"
#---------code to iteratively find the domain name------
def find_iterative(domain_name, req_id):
    #search the TLD name
    top_level_domain = domain_name.split(".")[-1]
    tld_server = None
    for x in range(len(dns_names)):
        if(dns_names[x] == top_level_domain):
            tld_server = values[x]

    # if TLD is not found just do a local search and rerturn results.
    if(tld_server == None):
        return lookup_ip(domain_name)
    else:
        return tld_server, "ns"

#---------code to recursively find the Domain name------
def find_recursive(domain_name, req_id):

    #search the TLD name
    top_level_domain = domain_name.split(".")[-1]
    tld_server = None
    for x in range(len(dns_names)):
        if(dns_names[x] == top_level_domain):
            tld_server = values[x]

    # if TLD is not found just do a local search and rerturn results.
    if(tld_server == None):
        return lookup_ip(domain_name)

    port = server_port
    # connect to the TLD server 1 or 2, must be removed
    ##
    #  --- remove these line when not running locally--
    if ":" in tld_server:
        parts = tld_server.split(":")
        tld_server = parts[0]
        port = int(parts[1])
    ##
    ##

    result = send_message(tld_server, port, domain_name, req_id, "rd")
    if( result != None and result != '' and (not result.startswith("ERROR"))):
        result_parts = result.split(" ")
        if (result_parts[4] == "aa"):
            result_parts[4] = "ra"
            return  result_parts[2], result_parts[4]
        elif(result_parts[4] == "nx"):
            return lookup_ip(domain_name)
        else:
            return  result_parts[2], result_parts[4]
    else:
       return lookup_ip(domain_name) 


#----------write the request string---------------------   

def write_request(domain_name, flag, req_id):
    return "0 " + domain_name + " " + str(req_id) + " " + flag

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
    if(flag == "rd"):
        result, flag = find_recursive(domain_name, req_id)
        return write_response(domain_name, result, flag, req_id)
    else:
        result, flag = find_iterative(domain_name, req_id)
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
    
    with open("rsresponses.txt", "w") as output_file:
        while True:
            print("[S]: Server is waiting for a connection...")
            connectionSocket, addr = serverSocket.accept()
            print(f"[S]: Client is connected at {addr}")
            data = connectionSocket.recv(200).decode('utf-8').strip()
            if not data:
                print(f'ERROR: Empty request')  
            else:
                print(f"<===== {data}")
                modifiedData = get_response(data.strip())
                print(f"======> {modifiedData}")
                if(modifiedData.startswith("ERROR") ):
                    print(modifiedData)
                else:
                    output_file.write(modifiedData + '\n')
                    output_file.flush() 
                connectionSocket.send(modifiedData.encode('utf-8'))
            connectionSocket.close()
    serverSocket.close()

#-------code to read from space separted file-----
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

#-------check if the result is an ipaddress
def is_valid_ipv4(ip):
    pattern = r"^(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
    return bool(re.match(pattern, ip))

#----main_program ----------------------

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

file_name = "rsdatabase.txt"  # Replace with your actual file
dns_names, values = populate_list_from_file(file_name)


if __name__ == "__main__":
    server(server_port)