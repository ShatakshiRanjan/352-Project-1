import socket
import sys

NO_IP = "0.0.0.0"
#----------write the request string---------------------   

def write_request(domain_name, flag, req_id):
    return "0 " + domain_name + " " + str(req_id) + " " + flag

#----------write the response string---------------------    

def write_response(domain_name, result, flag, req_id):
    return "1 " + domain_name + " " + result + " " + str(req_id) + " " + flag

def send_message(dns_host, port, domain_name, req_id, flag):
    print(f"connecting to client{dns_host}:{port}")
    response = write_response(domain_name, NO_IP, "nx", req_id)
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((dns_host, port))
        request = write_request(domain_name, flag, req_id)
        print(f"request====>{request}")
        client_socket.sendall(request.encode(), )
        response = client_socket.recv(200).decode()
        client_socket.close()
        print(f"response====>{response}")
        if(flag == "it"):
            response_parts = response.split(" ")
            # 1 njit.edu cheese.cs.rutgers.edu 16 ns
            dns_host = response_parts[2]
            if ":" in dns_host:
                parts = dns_host.split(":")
                dns_host = parts[0]
                port = int(parts[1])
            if(response_parts[4] == "ns"):
                response = send_message(dns_host, port, domain_name, (req_id +1), flag)
    except Exception as e:
        print(f"Exception while connecting to host:{dns_host}:{port}")
        print(f"Error: {e}")
    return response


def populate_list_from_file(filename):
    domain_names, flags = [], []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.split()  # Split by whitespace
                if len(parts) == 2:  # Ensure exactly two fields per line
                    domain_names.append(parts[0])
                    flags.append(parts[1])
                else:
                    print(f"Error: Invalid line: {line.strip()}")
        
        return domain_names, flags

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return [], []
    except Exception as e:
        print(f"An error occurred: {e}")
        return [], []

#----main_program ----------------------

server_port = 0
if len(sys.argv) != 3:
    print("Error: Missing Arguments. Correct syntax is python3 client.py rs_hostname rudns_port")
    sys.exit(1)
else:
    try:
       server_host =  sys.argv[1]
       server_port = int(sys.argv[2])
    except Exception:
        print(f"Error: Invalid port:{sys.argv[2]}")
        sys.exit(1) 

file_name = "hostnames.txt"  
domain_names, flags = populate_list_from_file(file_name)

with open("resolved.txt", 'w', encoding='utf-8') as output_file:
    for x in range(len(domain_names)):
        response = send_message( server_host, server_port, domain_names[x], 1, flags[x])
        output_file.write(response + "\n")
        output_file.flush()

print("ending the client..")  