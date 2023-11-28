import subprocess

from db_interact import *
FORMAT = 'UTF-8'
class Message:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.recv_argv = []
        self.recv_argc = 0
        self.send_argv = []
        self.send_argc = 0
        self._recv_buffer = b""
        self._send_buffer = b""
        self.header = None
        self.request = None
        self.response_created = False
    
    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def write(self):
        sent = self.sock.send(self._send_buffer)
        # print(self._send_buffer)
        self._send_buffer = self._send_buffer[sent:]

    
    def _create_message(self, response_type, res_code, res_msg, content_bytes, content):
        message = response_type + " " + str(res_code) + " " + res_msg + " " + str(content_bytes)
        if content_bytes:
            message = message + content
        return message

    def read(self):
        self._read()
        recv_data = self._recv_buffer.decode(FORMAT)
        # print(recv_data)

        request_info = recv_data.split()
        self.request = request_info[0]
        self.recv_argv = request_info[1:]
        self._recv_buffer = b""
        self.process_request()
    

    def close(self):
        # print(f"Closing connection to {self.addr}")
        try:
            self.sock.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.addr}: {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    
    def process_request(self):
        if(self.request != None):
            request = self.request
            argv = self.recv_argv
            res_code = None
            res_msg = None
            message = None
            if request == "check_ip":
                res_code, res_msg = self.reply_check_ip()
                message = self._create_message('RESPOND_CHECK_IP', res_code, res_msg, 0, "")
            elif request == "register":
                username = argv[0]
                password = argv[1]
                port = argv[2]
                res_code, res_msg = self.reply_register(username, password, port)
                message = self._create_message('RESPOND_REGISTER', res_code, res_msg, 0, "")
            elif request == 'login':
                password = argv[0]
                res_code, res_msg, username = self.reply_login(password)
                content = ""
                if res_code == 200:
                    content = "\nHello " + username
                message = self._create_message('RESPOND_LOGIN', res_code, res_msg, len(content), content)
            elif request == 'unregister':
                res_code, res_msg = self.reply_unregister()
                message = self._create_message('RESPOND_UNREGISTER', res_code, res_msg, 0, "")

            elif request == 'publish':
                fname = argv[0]
                lname = argv[1]
                size = int(argv[2])
                extension = argv[3]
                res_code, res_msg = self.reply_publish(fname, lname, size, extension)
                message = self._create_message('RESPOND_PUBLISH', res_code, res_msg, 0, "")
            elif request == 'unpublish':
                fname = argv[0]
                res_code, res_msg = self.reply_unpublish(fname)
                message = self._create_message('RESPOND_UNPUBLISH', res_code, res_msg, 0, "")
            elif request == 'view':
                res_code, res_msg, files_str = self.reply_view()
                message = self._create_message('RESPOND_VIEW', res_code, res_msg, len(files_str), files_str)

            elif request == 'fetch':
                fname = argv[0]
                res_code, res_msg, files_str = self.reply_fetch(fname)
                message = self._create_message('RESPOND_FETCH', res_code, res_msg, len(files_str), files_str)
    

            
            self.response_created = True
            self._send_buffer = message.encode(FORMAT)  

    def reply_check_ip(self):
        is_connected = check_ip_connected(self.addr[0])
        res_code = None
        res_msg = None
        if is_connected:
            res_code = 200
            res_msg = "\"This device has been registered, please sign in!\""
        else:
            res_code = 205
            res_msg = "\"You haven't register for this device, please register!\""
        return res_code, res_msg

    def reply_register(self, username, password, port):
        res_code = insert_account(username, password, self.addr[0], port)
        res_msg = None
        if res_code == 200:
            res_msg = "\"Register successfully!\""
        else:
            res_msg = "\"Username exists, please choose another username!\""
        return res_code, res_msg
    
    def reply_unregister(self):
        res_code = delete_account(self.addr[0])
        res_msg = "\"Delete account successfully!\""
        return res_code, res_msg
    

    def reply_login(self, password):
        res_code, username = check_account(password, self.addr[0])
        res_msg = None
        if res_code == 200:
            res_msg = "\"Login successfully!\""
        else:
            res_msg = "\"Incorrect password!\""
        return res_code, res_msg, username
    
    def reply_view(self):
        file_list = view_all_files(self.addr[0])
        res_code = 200
        res_msg = "View all your shared files"
        files_str = ""
        if len(file_list) == 0:
            files_str = "\n<empty>"
        else:
            for file in file_list:
                files_str += '\n'
                for element in file:
                    files_str += str(element) + " "
                files_str[:-1]
        return res_code, res_msg, files_str

    def reply_publish(self, fname, lname, file_size, extension):
        res_code = insert_file(fname, lname, file_size, extension, self.addr[0])
        res_msg = None
        if res_code == 200:
            res_msg = "\"Successfully add!\""
        if res_code == 201:
            res_msg = "\"You have already shared this file!\""
        if res_code == 202:
            res_msg = "\"Duplicate filename, please choose another name!\""
        return res_code, res_msg
    def reply_unpublish(self, fname):
        res_code = delete_file(fname, self.addr[0])
        res_msg = None
        if res_code == 200:
            res_msg = "\"Successfully delete!\""
        if res_code == 203:
            res_msg = "\"File not exist\""
        return res_code, res_msg
    def reply_fetch(self, fname):
        file_list = find_file_owner(fname, self.addr[0])
        res_code = None
        res_msg = None
        files_str = ""
        if len(file_list) == 0:
            res_code = 204
            res_msg = "\"No match file found!\""
        else:
            res_code = 200
            for file in file_list:
                #5: index of ip address in file (list type)
                print(file[5])
                is_owner_online = self.ping(str(file[5]))
                files_str += '\n'
                for element in file:
                    files_str += str(element) + " "
                if is_owner_online:
                    files_str += "online"
                else:
                    files_str += "offline"
            res_msg = f"\"Files founds: {len(file_list)}\""  
        return res_code, res_msg, files_str
    

    #### Ping function
    def ping(self, ipAddress):
        if check_ip_connected(ipAddress):
            command = ['ping', '-n', '1',ipAddress]
            return subprocess.call(command) == 0
        else: 
            print(f"The {ipaddress} IP address doesn't exist!")
            return False


    ####