import socket
import signal
import sys
import random
from urllib.parse import parse_qs

# Read a command line argument for the port where the server
# must run.
port = 8080
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    print("Using default port 8080")
hostname = socket.gethostname()

# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)

### Contents of pages we will serve.
# Login form
login_form = """
   <form action = "http://%s" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit" />
   </form>
"""
# Default: Login page.
login_page = "<h1>Please login</h1>" + login_form
# Error page for bad credentials
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
# Successful logout
logout_page = "<h1>Logged out successfully</h1>" + login_form
# A part of the page that will be displayed after successful
# login or the presentation of a valid cookie
success_page = """
   <h1>Welcome!</h1>
   <form action="http://%s" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
"""

#### Helper functions
# Printing.
def print_value(tag, value):
    print("Here is the", tag)
    print("\"\"\"")
    print(value)
    print("\"\"\"")
    print()

# Signal handler for graceful exit
def sigint_handler(sig, frame):
    print('Finishing up by closing listening socket...')
    sock.close()
    sys.exit(0)
# Register the signal handler
signal.signal(signal.SIGINT, sigint_handler)

# TODO: put your application logic here!
# Read login credentials for all the users
# Read secret data of all the users
# Read login credentials for all the users
user_passwords = {}
with open('passwords.txt') as f:
    for line in f:
        if line.strip():
            username, password = line.strip().split()
            user_passwords[username] = password

# Read secret data of all the users
user_secrets = {}
with open('secrets.txt') as f:
    for line in f:
        if line.strip():
            username, secret = line.strip().split()
            user_secrets[username] = secret

print("Loaded credentials:", user_passwords)
print("Loaded secrets:", user_secrets)

### Loop to accept incoming HTTP connections and respond.
while True:
    client, addr = sock.accept()
    req = client.recv(1024)

    # Let's pick the headers and entity body apart
    header_body = req.decode().split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    print_value('headers', headers)
    print_value('entity body', body)

    # TODO: Put your application logic here!
    # Parse headers and body and perform various actions
    # Parse the form data
    form_data = parse_qs(body)
    username = form_data.get("username", [None])[0]
    password = form_data.get("password", [None])[0]
    action = form_data.get("action", [None])[0]

    print("Parsed username:", username)
    print("Parsed password:", password)
    print("Parsed action:", action)

    # OPTIONAL TODO:
    # Set up the port/hostname for the form's submit URL.
    # If you want POSTing to your server to
    # work even when the server and client are on different
    # machines, the form submit URL must reflect the `Host:`
    # header on the request.
    # Change the submit_hostport variable to reflect this.
    # This part is optional, and might even be fun.
    # By default, as set up below, POSTing the form will
    # always send the request to the domain name returned by
    # socket.gethostname().
    submit_hostport = "%s:%d" % (hostname, port)

    # Default values
    html_content_to_send = login_page % submit_hostport
    headers_to_send = ''

    # Cookie/session storage - initialize only once outside the loop
    if 'active_tokens' not in globals():
        active_tokens = {}

    # Case A: Successful username/password login
    if username and password and username in user_passwords and user_passwords[username] == password:
        secret = user_secrets.get(username, "No secret found.")
        html_content_to_send = (success_page % submit_hostport) + secret

        # Generate cookie and store it
        rand_val = random.getrandbits(64)
        headers_to_send = f"Set-Cookie: token={rand_val}\r\n"
        active_tokens[rand_val] = username

    # Case B: Invalid login attempt
    elif (username or password):  # One or both are incorrect or missing
        html_content_to_send = bad_creds_page % submit_hostport

    # (Case: default login page already handled above)

    # (2) `headers_to_send` => add any additional headers
    # you'd like to send the client?
    # Right now, we don't send any extra headers.

    # Construct and send the final response
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    print_value('response', response)    
    client.send(response.encode())
    client.close()

    print("Served one request/connection!")
    print()

# We will never actually get here.
# Close the listening socket
sock.close()