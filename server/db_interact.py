'''Databae interaction is only for server'''
import mysql.connector
import ipaddress
import os

def connect_db():
    global mydb
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="ass1")
    global mycursor 
    mycursor = mydb.cursor(dictionary=True)

def insert_file(file_name, file_location, file_size, extension, ip):
    stored_ip = int(ipaddress.ip_address(ip))
    sql = '''SELECT fname, lname 
            FROM files
            WHERE owner = %s
        '''
    mycursor.execute(sql, (stored_ip, ))
    result = mycursor.fetchall()
    for file_info in result:
        if file_info['lname'] == file_location:
            return 201 #already share this file
    for file_info in result:
        if file_info['fname'] == file_name:
            return 202
    sql = "INSERT INTO files VALUES(%s, %s, %s, %s, %s)"
    val = (file_name, file_location, file_size, extension, stored_ip)
    mycursor.execute(sql, val)
    mydb.commit()
    return 200
def delete_file(file_name, ip):
    stored_ip = int(ipaddress.ip_address(ip))
    sql = '''SELECT fname
            FROM files
            WHERE owner = %s AND fname = %s
        '''
    mycursor.execute(sql, (stored_ip, file_name))
    myresult = mycursor.fetchall()
    if(len(myresult) == 0):
        return 203
    else:
        sql = '''DELETE FROM files
                WHERE owner = %s AND fname = %s
            '''
        mycursor.execute(sql, (stored_ip, file_name))
        mydb.commit()
        return 200
    
def find_file_owner(file_name, ip):
    stored_ip = int(ipaddress.ip_address(ip))
    split_tup = os.path.splitext(file_name)
                #Get file extension
    file_head = split_tup[0]
    file_extension = split_tup[1]
    pattern = f"\b*{file_head}.*{file_extension}$"
    sql = '''SELECT fname, lname, filesize, extension , username, IPAddress, port
            FROM files, peer
            WHERE peer.IPAddress = files.owner && files.fname REGEXP %s'''

    mycursor.execute(sql, (pattern, ))
    result = mycursor.fetchall()
    ret_list = []
    for file in result:
        username = None
        if file["IPAddress"] == stored_ip:
            username = "YOU"
        else:
            username = file["username"]
        ip = ipaddress.ip_address(file["IPAddress"])
        ret_list.append([file["fname"], file["lname"], file["filesize"], file["extension"], username, ip, file["port"]])
        
    return ret_list

def check_ip_connected(ip):
    stored_ip = int(ipaddress.ip_address(ip))
    sql = '''SELECT *
            FROM peer
            WHERE IPAddress = %s'''
    mycursor.execute(sql, (stored_ip, ))
    result = mycursor.fetchall()
    return len(result) == 1

def insert_account(username, password, ip, port):
    stored_ip = int(ipaddress.ip_address(ip))
    sql = '''SELECT *
            FROM peer
            WHERE username = %s'''
    mycursor.execute(sql, (username, ))
    result = mycursor.fetchall()
    if len(result):
        return 206
    else:
        sql = "INSERT INTO peer VALUES(%s, %s, %s, %s)"
        val = (username, password, stored_ip, port)
        mycursor.execute(sql, val)
        mydb.commit()
        return 200
    
def delete_account(ip):
    stored_ip = int(ipaddress.ip_address(ip))
    sql = '''DELETE FROM peer
                WHERE IPAddress = %s
            '''
    mycursor.execute(sql, (stored_ip, ))
    mydb.commit()
    return 200 

def check_account(password, ip):
    stored_ip = int(ipaddress.ip_address(ip))
    sql = '''SELECT username
            FROM peer
            WHERE IPAddress = %s && password = %s'''
    mycursor.execute(sql, (stored_ip, password))
    result = mycursor.fetchall()
    if len(result):
        return 200, str(result[0]['username'])
    else:
        return 207, ""

def view_all_files(ip):
    stored_ip = int(ipaddress.ip_address(ip))
    sql = '''SELECT fname, lname, filesize, extension
            FROM files
            WHERE owner = %s'''
    mycursor.execute(sql, (stored_ip, ))
    result = mycursor.fetchall()
    ret_list = []
    for file in result:
        ret_list.append([file["fname"], file["lname"], file["filesize"], file["extension"]])
    return ret_list

   


def close_connect():
    mydb.close()

