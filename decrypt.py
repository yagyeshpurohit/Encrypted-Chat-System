import hashlib
import random
import socket
from Crypto.Cipher import DES3
import base64



server_ip = '127.87.34.12'
application_port = 9825
ADDR = (server_ip, application_port)





def generate_nonce():
    return str(random.randint(0,1000000000))

def pad(text):
    while len(text) % 8 !=0:
        text += ' '
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


     

''' CREATING A SECRET KEY '''   

roll_no = "2020201865"
randomNonce = generate_nonce()
secret_key = hashlib.sha256((roll_no+randomNonce).encode())
secret_key = int.from_bytes(secret_key.digest(), 'big') # converting it to int
generator = 2
prime_hex = 'FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF'
prime = int(prime_hex,16)

public_key = pow(generator,secret_key,prime)
public_key = str(public_key)






serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(ADDR)
serversocket.listen()

newsocket, cliaddr = serversocket.accept()

''' DH key exchange'''
public_key_sender = newsocket.recv(4096).decode()
newsocket.send(public_key.encode())

public_key_sender = int(public_key_sender)
shared_public_key = pow(public_key_sender,secret_key,prime)
shared_public_key_24b = str(shared_public_key)[:24]

''' Decryption '''
# sender_msg = newsocket.recv(4096)
# sender_msg = decryptMsg(sender_msg, shared_public_key_24b)

# filename = 'snippet.pdf'
# with open(filename, 'wb') as file:
#     file.write(sender_msg)

sender_msg = newsocket.recv(4096)
sender_msg = decryptMsg(sender_msg, shared_public_key_24b)
sender_msg = sender_msg.decode()
sender_msg = unpad(sender_msg)
print('Msg received: ' + sender_msg)

print('receiver private key: ' + shared_public_key_24b)
newsocket.close()


serversocket.close()


