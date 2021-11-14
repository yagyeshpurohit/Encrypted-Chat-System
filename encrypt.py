import hashlib
import random
import socket
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
import base64
import os


server_ip = '127.87.34.12'
application_port = 9825
ADDR = (server_ip, application_port)





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
    return d.decode()
     
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
        


secret_key = ''
roll_no = "2020201013"    
randomNonce = generate_nonce()
generator = 2
secret_key = hashlib.sha256((roll_no+randomNonce).encode()) # secret_key of hash type
secret_key = int.from_bytes(secret_key.digest(), 'big') # converting it to int   
prime_hex = 'FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF'
prime = int(prime_hex,16)
public_key = pow(generator,secret_key,prime)
public_key = str(public_key)

    


''' CREATING A SECRET KEY '''   

# group_nonce = DES3.adjust_key_parity(get_random_bytes(24))
# print(group_nonce)



# secret_key = str(secret_key)[:8]  #converting the same secret_key to str for reducing its size
# print(secret_key)
# secret_key = int(secret_key)    # converting it back to int for calculation purpose





#print('my public key : ' + public_key + 'of len: ' + str(len(public_key)))


msg = input("Enter message: ")
#encrypted_msg = encryptMsg(msg, key)


clisocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clisocket.connect(ADDR)

clisocket.send(public_key.encode())
'''DH key exchange '''
public_key_receiver = clisocket.recv(4096).decode()
public_key_receiver = int(public_key_receiver, 10)
shared_public_key = pow(public_key_receiver,secret_key,prime)
shared_public_key_24b = str(shared_public_key)[:24]

print('sender private key: ' + shared_public_key_24b)

'''Encryption '''
#data = readFile('aadhar_1.pdf')
encrypted_msg = encryptMsg(msg, shared_public_key_24b)

clisocket.send(encrypted_msg)
clisocket.close()




    #   FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF