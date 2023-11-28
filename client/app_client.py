from libclient import Client
from cmd import Cmd
import socket
import os
import sys
import threading
from getpass import getpass

# sel = selectors.DefaultSelector()

SERVER_PORT = 5050
LIS_PORT = 9999
# HOST = socket.gethostbyname(socket.gethostname())
HOST = "127.0.0.1"
SERVER = "127.0.0.1"
FORMAT = 'UTF-8'



class MyCmd(Cmd):
    def __init__(self, *args, client, sock):
        super().__init__(args)
        self.client = client
        self.sock = sock
    prompt = "> "
    
    def do_help(self, args):
        arglist = args.split()
        if len(arglist) != 0:
            print('Wrong format')
        else:
            data = "--------------------------------------------------------\n"
            data += "view: List all the files from the server.\n"
            data += "unregister: Delete your account.\n"
            data += "logout: Log out from the system\n"
            data += "publish: Share a file with other peers\n"
            data += "unpublish: Stop sharing a file with other peers\n"
            data += "view: Show all your sharing files\n"
            data += "fetch: fetch a file from other peer\n"
            data += "help: List all the commands.\n"
            data += "--------------------------------------------------------\n"
            print(data)
    def do_view(self, args):
        arglist = args.split()
        if len(arglist) != 0:
            print('Wrong format')
        else:
            self.client.request = 'view'
            self.client.write()
            self.client.read()
    
    def do_publish(self, args):
        arglist = args.split()
        if len(arglist) != 2:
            print('Wrong format')
        else:
            path = arglist[1]
            if not os.path.isfile(path):
                print("File path does not exist!")
            else:
                self.client.request = 'publish'
                file_size = os.path.getsize(path)
                split_tup = os.path.splitext(path)
                #Get file extension
                file_extension = split_tup[1]
                arglist.append(file_size)
                arglist.append(file_extension)
                self.client.request_argv = arglist
                self.client.write()
                self.client.read()
    def do_unpublish(self, args):
        arglist = args.split()
        if len(arglist) != 1:
            print('Wrong format')
        else:
            value = args
            self.client.request = 'unpublish'
            self.client.request_argv = [value]
            # sel.select(timeout=None)
            self.client.write()
            self.client.read()

    def do_fetch(self, args):
        arglist = args.split()
        if len(arglist) != 1:
            print('Wrong format')
        else:
            self.client.request = 'fetch'
            self.client.request_argv = [args]
            self.client.write()
            self.client.read()

    def do_unregister(self, args):
        arglist = args.split()
        if len(arglist) != 0:
            print('Wrong format')
        else:
            self. client.request = 'unregister'
            self.client.write()
            self.client.read()
            sys.exit()
    

    def do_logout(self, args):
        # self.sock.close()
        # raise Exception("logout")
        return True
    def do_exit(self, args):
        sys.exit()


##### Wait for peer connect (request to send file)
def send_file(conn, addr):
    msg = conn.recv(4096).decode(FORMAT)
    print(msg)
    msg_list = msg.split()
    request_type = msg_list[0]
    if request_type == "FILE":
        lname = msg_list[1]
        check_path = os.path.isfile(lname)
        if not check_path:
            conn.send("RESPOND_FILE 301 \"Fetch file fail!\" 0".encode(FORMAT))
            print(f"Close connection to {addr}")
            conn.close()
        else:
            file = open(lname, "rb")
            data = file.read()
            conn.sendall(data)
            conn.send("RESPOND_FILE 300 \"Fetch file successfully!\" 5\n<END>".encode(FORMAT))
            file.close()
            print(f"Close connection to {addr}")
            conn.close()

def listen(addr_listen):
    while True:
        sock_listen.listen()
        print(f"Client listen on {addr_listen}....\n")
        conn, addr = sock_listen.accept()
        print(f"Accepted connection from {addr}")
        new_thread = threading.Thread(target=send_file, args=(conn, addr))
        new_thread.start()
    

  
if __name__ == "__main__":
    ##Check account exist
    addr = (SERVER, SERVER_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.setblocking(False)
    sock.setblocking(True)
    sock.connect_ex(addr)
    client = Client(sock, addr)
    print(f"Starting connection to {addr}")
    client.request = "check_ip"
    client.write()
    res_code = client.read()
    if res_code != 200:
        while True:
            print("Type \"exit\" to exit, or press Enter to register...")
            a = input("> ")
            if a == "exit":
                sys.exit()
            if a == "":
                print(">register:")
                username, password = None, None
                while True:
                    username = input("Username: ")
                    if ' ' in username:
                        print('White space is not accepted')
                    else:
                        break

                while True:
                    password = getpass(prompt="Password: ")
                    if ' ' in password:
                        print('White space is not accepted')
                    else:
                        break
                
                repeat_password = getpass(prompt="Repeat password: ") 
                if password != repeat_password:
                    print("Unmatched password!")
                    continue
                client.request = "register"
                client.request_argv = [username, password, LIS_PORT]
                client.write()
                res_code = client.read() 
                if res_code == 206:
                    continue
                break
            print("Wrong command!")

    ##Start listen to file request
    addr_listen = (HOST, LIS_PORT)
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_listen.setblocking(True)
    sock_listen.bind(addr_listen)

    listen_thread = threading.Thread(target=listen, args=(addr_listen,))
    listen_thread.daemon = True

    listen_thread.start()
    
    
    while True:
        print("Type \"exit\" to exit, or press Enter to login...")
        a = input("> ")
        if a == "exit":
            sys.exit()
        if a == "":
            print(">login:")
            password = getpass(prompt="Password: ")
            client.request = "login"
            client.request_argv = [password]
            client.write()
            res_code = client.read()
            if res_code != 200:
                continue
            ####Connect to server
            try:
                app = MyCmd(client=client,sock=sock)
                app.cmdloop('Enter a command to do something.')
            except Exception as e:
                pass
        else:
            print("Wrong command!")    

    
    
    

    ####Waiting for send file request
    

    
