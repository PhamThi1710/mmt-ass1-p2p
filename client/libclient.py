import socket
import traceback
import os
FORMAT = 'UTF-8'

class Client:
    def __init__(self, sock, addr, request=None):
        self.sock = sock
        self.addr = addr
        self.request = request
        self.request_argv = []
        self._recv_buffer = b""
        self._send_buffer = b""
        self.receive_response = False
        self.file_owner_list = {}
        self.request_file = False
        self.requested_owner = None
        self.request_fname = None

    def _read(self):
        
        try:
            # Should be ready to read
            data = None
            if self.request_file:
                file_bytes = b""
                done = False
                i = 0
                while not done:
                    data = self.requested_owner.recv(1024)
                    if file_bytes[-5:] == b"<END>":
                        done = True
                    else:
                        if i == 0 and file_bytes[:12] == b"RESPOND_FILE":
                            data = file_bytes
                            break
                        file_bytes += data
                if done:
                    data = file_bytes[-51:]
                    file_bytes = file_bytes[:-51]
                    split_tup = os.path.splitext(self.request_fname)
                    #Get file extension
                    saved_name = split_tup[0]
                    extension = split_tup[1]
                    if os.path.isdir("./download"):
                        os.makedirs("./download")
                    with open("./download/" + saved_name + "(copy)" + extension, "wb") as file:            
                        file.write(file_bytes)
                    
            else:
                data = self.sock.recv(4096)
            
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            return 1
        else:
            # print(f"data: {data}")
            if data:
                # print(f"data: {data}")
                self._recv_buffer += data
                self.request_file = False
                return 0
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            sent = None
            try:
                # print(self._send_buffer)
                # Should be ready to write
                if self.request_file:
                    sent = self.requested_owner.send(self._send_buffer)
                else:
                    sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                self.request = None
                self.request_argv = []

   
    def read(self):
        while self._read():
            continue
        if self._recv_buffer:
            lines = self._recv_buffer.decode(FORMAT).split('\n')
            header_list = lines[0].split()
            respond_type = header_list[0]
            respond_code = header_list[1]
            content_len = header_list[-1]
            message = " ".join(header_list[1:-1])
            
            print("Type: " + respond_type)
            print("Code: " + respond_code)
            print("Message: " + message)
            if int(content_len):
                print("Content length: " + content_len)
                if respond_type == "RESPOND_FETCH":
                    count = 1
                    print ('{:>5} {:>12} {:>12}  {:>12} {:>12} {:>12}'.format("NO.", "FILE", "TYPE", "SIZE", "OWNER", "STATUS"))
                    for content_line in lines[1:]:
                        args_list = content_line.split()
                        file_name = args_list[0]
                        file_path = args_list[1]
                        file_size = args_list[2]
                        file_extension = args_list[3]
                        owner = args_list[4]
                        owner_ip = args_list[5]
                        owner_port = args_list[6]
                        owner_status = args_list[7]
                        print ('{:>5} {:>12} {:>12}  {:>12} {:>12} {:>12}'.format(count, file_name, file_extension, file_size, owner, owner_status))
                        if owner_status == 'online' and owner != 'YOU':
                            self.file_owner_list[str(count)] = [owner_ip, owner_port, file_name, file_path]
                        count += 1
                elif respond_type == "RESPOND_VIEW":
                    count = 1
                    print ('{:>5} {:>20} {:>40}  {:>7} {:>12} '.format("NO.", "FILE", "LOCATION", "TYPE", "SIZE"))
                    content = lines[1:]
                    if(content[0] == "<empty>"):
                        print(content[0])
                    else:
                        for line in lines[1:]:
                            args_list = line.split()
                            file_name = args_list[0]
                            file_path = args_list[1]
                            file_size = args_list[2]
                            file_extension = args_list[3]
                            print ('{:>5} {:>20} {:>40}  {:>7} {:>12}'.format(count, file_name, file_path, file_extension, file_size))
                            count += 1
    
                else:
                    print(lines[1])
            self._recv_buffer = b""
            self.receive_response = True
            if int(content_len) and respond_type == "RESPOND_FETCH":
                self.choose_peer()
            if self.request_file:
                self.request_file = False
            if not self.request_file:
                self.request_fname = None
                self.requested_owner = None
            return int(respond_code) 
        else:
            return -1


    def write(self):
        if self._send_buffer:
            self._send_buffer = b""
        send_msg = self.request
        for arg in self.request_argv:
            send_msg = send_msg + " " + str(arg)
        self._send_buffer = send_msg.encode(FORMAT)
        self._write()

    def choose_peer(self):
        print("Type online owner number you want to fetch file. Type \"exit\" if you don't want to fetch")
        while True:
            user_input = input(">Choose file> ")
            if user_input == "exit":
                self.file_owner_list = {}
                break
            else:
                try:
                    peer = self.file_owner_list[user_input]
                    self.file_owner_list = {}
                    self.request_file_from_peer(peer)
                    break
                except Exception:
                    print("Invalid: Please choose online owner no.")
    
    def request_file_from_peer(self, peer):
        self.request_file = True
        self.request_fname = peer[2]
       
        sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.requested_owner = sender
        #peer = [owner_ip, owner_port, file_name, file_path]
        try:
            self.requested_owner.connect((peer[0], int(peer[1])))
        except Exception:
            print(
                f"Main: Error: Exception for {(peer[0], peer[1])}:\n"
                f"{traceback.format_exc()}"
                )
        self.request = "FILE"
        self.request_argv = [peer[3]]

        self.write()
        self.read()       







