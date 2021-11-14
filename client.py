##COMMAND FOR SIGNUP - SIGNUP <USERNAME> <PWD> (works with lowercase as well)
## COMMAND FOR LOGIN - LOGIN <USERNAME> <PWD>
## COMMAND FOR SENDING MSG TO GROUP - SENDGROUP <GROUP_NAME> <MSG> 
## COMMAND FOR SENDING MSG TO PEER - SEND <USERNAME> <MSG>
##structure of the data received from server  :   MSG + ";" + SENDER + ";" + COMMAND(send/login/signup etc)  - for send command
#                                                 MSG + ";" + COMMAND  - for other commands 

import socket
import sys
import threading
import hashlib
import random
from Crypto.Cipher import DES3
import os


SEPERATOR = ";"
msg = ''
PORT = 12346
public_key = ''

message = ''
def signup(username,pwd) :
	global current_user
	global roll_no
	name = input("Enter name :")
	roll_no = input("Enter roll no. :  ")

	''' Creating a Secret Key '''
	randomNonce = generate_nonce()
	secret_key = hashlib.sha256((roll_no + randomNonce).encode())
	secret_key = int.from_bytes(secret_key.digest(), 'big') # converting it to int
	generator = 2
	prime_hex = 'FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF'
	prime = int(prime_hex,16)

	public_key = pow(generator,secret_key,prime)
	public_key = str(public_key)
	msg = "signup;" + username + SEPERATOR + pwd +  SEPERATOR + name +  SEPERATOR + roll_no + SEPERATOR + public_key
	current_user = username 
	client_sock.send(msg.encode())



def login(username,pwd) :
	global current_user
	msg = "login;" + username +  SEPERATOR + pwd 
	current_user = username
	client_sock.send(msg.encode())



def createGroup(group_name) :
	msg = "create;" + group_name 
	client_sock.send(msg.encode())


def joinGroup(group_name) :
	msg = "join;" + group_name + SEPERATOR + current_user
	client_sock.send(msg.encode())


def listGroups() :
	msg = "list;" 
	client_sock.send(msg.encode())


def sendMsgToPeer(username) :
	msg = "send;" + username + SEPERATOR + current_user
	client_sock.send(msg.encode())


def sendMsgToGroup(group_name,msg) :
	msg = "sendgroup;" + group_name + SEPERATOR + msg + SEPERATOR + current_user
	client_sock.send(msg.encode())

def sendMsg(recv_key):
	encrypted_msg = encryptMsg(message, public_key)
	client_sock.send(encrypted_msg.encode())

def receiveMsg(sender_key):
	encrypted_msg = client_sock.recv(4096)
	decrypted_msg = decryptMsg(encryptMsg, sender_key)
	decrypted_msg = decrypted_msg.decode()
	print(decrypted_msg)

def receive():
	while True:
		data = client_sock.recv(1024).decode()
		parts = data.split(";")
		temp = 0
		command = parts[-1]
		if(command == 'list') :
			groups = parts[0].split(":")
			for i in groups :
				print(i)
		elif(command == 'send') :
			sender = parts[1]
			msg = parts[0]
			print(sender + " : " + msg)

		elif(command == 'senderkey') :
			sender_public_key = parts[1]
			receiveMsg(sender_public_key)

		elif(command == 'receiverkey') :
			receiver_public_key = parts[1]
			sendMsg(receiver_public_key)

		else :
			print(parts[0])
		
		


#Thread function for receiving data from server 
# def receive():
#     while True:
#         data = client_sock.recv(1024).decode()
# 		parts = data.split(";")
# 		temp = 0
# 		command = parts[-1]
# 		if(command == 'list') :
# 			groups = parts[0].split(":")
# 			#print all the groups 
# 			for i in groups :
# 				print(i)
# 		elif(command == 'send') :
# 			sender = parts[1]
# 			msg = parts[0]
# 			print(sender + " : " + msg)
# 		elif(command == 'senderkey') :
# 			sender_public_key = parts[1]
# 			receiveMsg(sender_public_key)
		
# 		elif(command == 'receiverkey') :
# 			receiver_public_key = parts[1]
# 			sendMsg(receiver_public_key)
# 		else :
# 			print(parts[0])

        

#Thread for sending data to server
def write():
    while True :
    	inp = input()
    	parts = (inp.strip()).split(' ')
    	command = parts[0].lower()
    	if(command == 'signup') :
    		signup(parts[1],parts[2])
    	elif(command == 'login') :
    		login(parts[1],parts[2])
    	elif(command == 'join') :
    		joinGroup(parts[1])
    	elif(command == 'create') :
    		createGroup(parts[1])
    	elif(command == 'list') :
    		listGroups()
    	elif(command == 'send') :
    		n = len(parts)
    		message = ''
    		for i in range(2,n) :
    			message += parts[i] + ' '
    		sendMsgToPeer(parts[1])
    	elif(command == 'sendgroup') :
    		n = len(parts)
    		msg = ''
    		for i in range(2,n) :
    			msg += parts[i] + ' '
    		sendMsgToGroup(parts[1],msg)


def generate_nonce():
    return str(random.randint(0,1000000000))

def pad(text):
    while len(text) % 8 !=0:
        text += '*'
    return text

def unpad(text):
    return text.rstrip('*')

def encryptMsg(message, key):
    message = pad(message)
    cipher = DES3.new(key, DES3.MODE_ECB)
    m = cipher.encrypt(message)
    # n = base64.b64encode(m)
    return m

def decryptMsg(cipher_text, key):
    cipher = DES3.new(key , DES3.MODE_ECB)
    d = cipher.decrypt(cipher_text)
    return d


def readFile(filename):
    try:
        with open(filename , 'r+b') as file:
            filedata = file.read()
            filesize = os.path.getsize(filename)
            print(filesize)
            if filesize % 8 !=0:
                pad_size = 8 - (filesize%8)
            else:
                pad_size = 0
            print(pad_size)
            for i in range(pad_size):
                filedata += b'0'
            
    except FileNotFoundError:
        print("Requested File Not Found!!")
    return filedata
   




client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	client_sock.connect((socket.gethostname(), PORT))
except Exception as e :
	raise SystemExit(f"Connection failed : {e}")


# '''DH key exchange '''
# public_key_receiver = client_sock.recv(4096).decode()
# public_key_receiver = int(public_key_receiver, 10)
# shared_public_key = pow(public_key_receiver,secret_key,prime)
# shared_public_key_24b = str(shared_public_key)[:24]

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()