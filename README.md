#  A simple file-sharing P2P application using the TCP/IP protocol stack in Python
---- Assignment 1 for the Computer Network course ---- <br />
A multithreaded file transfer client-server program build using a Python programming language that a client informs the server as to what files are contained in its local repository but does not actually transmit 
file data to the server and when a client requires a file that does not belong to its repository, a request is sent to the server. The server identifies some other clients who store the requested file and sends their identities to the requesting client. The client will select an appropriate source node and the file is then directly fetched by the requesting client from the node that has a copy of the file without requiring any server intervention. <br />

The server supports the following functions: <br />

PUBLISH fname lname : A local file (which is stored in the client's file system at lname) is added to the client's repository as a file named fname and this information is conveyed to the server. <br />
FETCH fname: Fetch some copy of the target file and add it to the local repository. <br />
VIEW: List all the shared files from the server. <br />
UNPUBLISH fname: Unpublish a shared file from the server. <br />
REGISTER: Create a new account. <br />
LOGIN: Log in to the application. <br />
UNREGISTER: Delete an account. <br />
LOGOUT: Disconnect from the server. <br />
HELP: List all the commands. <br />

and two functions for their own in terminal: <br />

PING <hostname>:live check the host named hostname. <br />
DISCOVER <hostname>: discover the list of local files of the host named hostname.

