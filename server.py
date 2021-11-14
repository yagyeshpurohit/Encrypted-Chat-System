import socket
import threading
import os
import sys
 

groups = []  #list of group objects
clients = []  #list of client objects
sockets_list = {}  #active sockets(clients) {username : socket}
public_keys = {}

SEPERATOR = ";"
PORT = 12346
recv_sock = 0

class Group :
	def __init__(self,group_name,participants,group_secret) :
		self.group_name = group_name
		self.participants = []
		self.group_secret = group_secret

	def addParticipants(self,participant) :
		self.participants.append(participant)


class Clients :
	def __init__(self,name,roll_no,username,password,client_sock) :
		self.name = name
		self.roll_no = roll_no
		self.username = username
		self.password = password
		self.client_sock = client_sock

#helper function to get socket by its username
def getSocket(username) :
	for key in sockets_list :
		if(key == username) :
			return sockets_list[key][0]



def signup(info, client_sock) :
	global new_client
	username = info[1]
	#print(username)
	msg = ''
	#Check if user already exists :
	if(not any(x.username == username for x in clients)) :
		password = info[2]
		name = info[3]
		roll_no = info[4]
		public_key = info[5]
		new_client = Clients(name,roll_no,username,password,client_sock)
		clients.append(new_client)
		sockets_list[username] = [client_sock, public_key]
		msg = "Signed up successfully!"
	else :
		msg = "User already exists"
	print(msg)
	return msg


def login(info,client_sock) :
	username = info[1]
	pwd = info[2]
	if(username in sockets_list) :
		msg = "user already logged in"
		return msg
	#sockets_list[username] = client_sock
	if(any(x.username == username for x in clients)) :
		flag = False
		for x in clients :
			if(x.username == username and x.password == pwd) :
				msg = "logged in successfully"
				flag = True
		if(not flag) :
			msg = "Wrong credentials"

	else :
		msg = "User doesn't exist"
	print(msg)
	return msg


#create new group
def createGroup(info) :
	#global new_group
	
	group_name = info[1]
	participants = []
	group_secret = 0
	msg = ''
	if(any(x.group_name == group_name for x in groups)) :
		msg = "Group already exists"
	else :
		new_group = Group(group_name,participants,group_secret)
		groups.append(new_group)
		msg = "Group created successfully"
	print(msg)
	return msg


#Join a group
def joinGroup(info) :
	#global new_group
	group_name = info[1]
	member = info[2]
	flag = False
	msg = ''
	group_secret = 0
	#group doesn't exist --- create a new group
	for x in groups :
		if(x.group_name == group_name) :
			x.participants.append(member)
			flag = True
			break
	if(not flag) :
		print("group doesn't exist")
		participants = []
		new_group = Group(group_name,participants,group_secret)
		new_group.participants.append(member)
		groups.append(new_group)

	msg = "group joined successfully"
	return msg


#List all the available groups
def listGroups() :
	msg = ''
	if(len(groups) > 0) :
		for x in groups :
			msg += x.group_name
			msg += ':'
	else :
		msg = "No group found!"
	print(msg)
	return msg


def sendMsgToPeer(info) :
	receiver  = info[1]
	
	sender = info[2]
	flag = False   #to check whether the receiver exists 
	client_sock = ''


	#retrieving client socket: 
	for key in sockets_list :
		if(key == receiver) :
			flag = True
			recv_sock = sockets_list[key][0]
			public_key_receiver = sockets_list[key][1]
			
		if(key == sender) :
			flag = True
			sender_sock = sockets_list[key][0]
			public_key_sender = sockets_list[key][1]
		
	#if recevier exists - send msg
	if(flag) :
		recv_msg = public_key_sender + ';senderkey'
		recv_sock.send(recv_msg.encode())

		sender_msg =public_key_receiver + ';receiverkey'
		sender_sock.send(sender_msg.encode())

		data = sender_sock.recv(4096)
		recv_sock.send(data)

		# msgToSend +=  SEPERATOR + sender + SEPERATOR + "send" 
		# client_sock.send(bytes(msgToSend,"utf-8"))
		msg = "message sent successfully"
	else :
		msg = "username doesn't exist"
	print(msg)
	return msg


def sendMsgToGroup(info) :
	group_name = info[1]
	msgToSend = info[2]
	sender = info[3] 
	flag = False  #to check if group exists
	senderIsMember = False  #to check if sender is the member of the group
	msg = ''
	msgToSend += SEPERATOR + sender + SEPERATOR + "send"
	for x in groups :
		if(x.group_name == group_name) :
			flag = True
			for username in x.participants :
				if(username == sender) :
					senderIsMember = True
					continue
				client_sock = getSocket(username)
				client_sock.send(bytes(msgToSend,"utf-8"))
	if(not flag) :
		msg = "group doesn't exist"
	if(not senderIsMember) :
		msg = "sender is not the member of the group"
	msg = "message sent successfully"
	print(msg)

	return msg



#create new client
def newClient(client_sock,addr) :
	while True :
		msg = ''
		data = client_sock.recv(1024).decode()
		info = data.split(";")
		command = info[0].lower()
		if(command == 'signup') :
			msg = signup(info,client_sock)
			msg += SEPERATOR + "signup"
		elif(command == 'login') :
			msg = login(info,client_sock)
			msg += SEPERATOR + "login"
		elif(command == 'join') :
			msg = joinGroup(info)
			msg += SEPERATOR + "join"
		elif(command == 'create') :
			msg = createGroup(info)
			msg += SEPERATOR + "create"
		elif(command == 'list') :
			msg = listGroups()
			msg += SEPERATOR + "list"
		elif(command == 'send') :
			msg = sendMsgToPeer(info)
		elif(command == 'sendgroup') :
			msg = sendMsgToGroup(info)
		
		client_sock.send(bytes(msg,"utf-8"))
		
	client_sock.close()





#main() CODE 
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((socket.gethostname(), PORT))
server_sock.listen()
while True :
	try :
		client, addr = server_sock.accept()
		#new thread for every client
		threading._start_new_thread(newClient,(client,addr))
	except KeyboardInterrupt as e :
		print("server shutting down")
		server_sock.close()
		sys.exit(0)








