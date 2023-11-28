import socket
import traceback
import threading
import subprocess
from cmd import Cmd 
import libserver
from db_interact import *
PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# HOST = socket.gethostbyname(socket.gethostname())
HOST = "127.0.0.1"
FORMAT = 'UTF-8'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))


def checkquery(query):
    mycursor.execute(query)
    getAccount = mycursor.fetchone()
    if getAccount:
        return True
    else:
        return False
def ping(hostname):
    try:
        ip = ipaddress.ip_address(hostname)
    except:
        print(f"The {hostname} IP address doesn't exist!")
        return False
    else:
        if check_ip_connected(hostname):
            command = ['ping', '-n', '1',hostname]
            return subprocess.call(command) == 0
        else: 
            print(f"The {hostname} IP address doesn't exist!")
            return False

def discover(hostname):
    try:
        ip = ipaddress.ip_address(hostname)
    except:
        print(f"The {hostname} IP address doesn't exist!")
        return False
    else:
        if check_ip_connected(hostname):
            files = view_all_files(hostname)
            count = 1
            print ('{:>5} {:>20} {:>40}  {:>7} {:>12} '.format("NO.", "FILE", "LOCATION", "TYPE", "SIZE"))
            if(len(files) == 0):
                print("<empty>")
            else:
                for file in files:
                    file_name = file[0]
                    file_path = file[1]
                    file_size = file[2]
                    file_extension = file[3]
                    print ('{:>5} {:>20} {:>40}  {:>7} {:>12}'.format(count, file_name, file_path, file_extension, file_size))
                    count += 1
        else:
            response_data = "The " + str(hostname) + " IP address doesn't exist"
            print(response_data)


class MyCmd(Cmd):
    prompt = "> "
    def do_help(self, args):
        arglist = args.split()
        if len(arglist) != 0:
            print('Wrong format')
        else:
            data = "[COMMAND]--------------------------------------------------------\n"
            data += "ping <hostname>: live check the host named hostname\n"
            data += "discover <hostname>: discover the list of local files of the host named hostname\n"
            data += "exit: Get out of command tasks\n"
            data += "[COMMAND]--------------------------------------------------------\n"
            print(data)
    def do_ping(self, args):
        arglist = args.split()
        if len(arglist) != 1:
            print('Wrong format')
        else:
            host = arglist[0]
            print(ping(host))
    def do_discover(self, args):
        arglist = args.split()
        if len(arglist) != 1:
            print('Wrong format')
        else:
            host = arglist[0]
            discover(host)
    def do_exit(self, args):
        raise SystemExit()


def client_connect(conn, addr):
    try:
        # print(f"Accepted connection from {addr}")
        message = libserver.Message(conn, addr)
        try:
            while True:
                message.read()
                message.write()
        except Exception:
            print(
                f"Main: Error: Exception for {message.addr}:\n"
                f"{traceback.format_exc()}"
                )
            message.close()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
def command():
    app = MyCmd()
    app.cmdloop('Enter a command to do something.')


if __name__ == "__main__":
    try:
        connect_db()
        #Thread for server command line
        command_thread = threading.Thread(target= command, args=())
        command_thread.start()
        
        #Wait for client connected
        while True:
            sock.listen()
            # print(f"Listening on {(HOST, PORT)}")
            sock.setblocking(True)
            conn, addr = sock.accept()
            new_thread = threading.Thread(target=client_connect, args=(conn,addr))
            new_thread.start()

    except KeyboardInterrupt:
        close_connect()
        print("Caught keyboard interrupt, exiting")
