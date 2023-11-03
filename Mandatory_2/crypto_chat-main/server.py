#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
import argparse
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
"""------------ Below this line is changes ------------"""
import nacl.utils
import nacl.secret
from nacl.public import PrivateKey, Box




#Serveren laver en symmetrisk key
server_s_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
def key_exchange(client):
    """Handles key exchange with the client"""
    global server_s_key
    global server_s_box
    pk_client = nacl.public.PublicKey(client.recv(BUFSIZ))
    #Laver public og private key
    sk_server = PrivateKey.generate()
    pk_server = sk_server.public_key
    server_box = Box(sk_server, pk_client)
    #Sender dens public key til client.
    client.send(bytes(pk_server))
    #Laver en box med den symmetriske key
    server_s_box = nacl.secret.SecretBox(server_s_key)
    #Den symmetriske key bliver krypteret med serveren private key.
    encrypted = server_box.encrypt(server_s_key)
    #Der bliver generet en NONCE
    nonce = nacl.utils.random(Box.NONCE_SIZE)
    #Den krypteret symmetriske key og NONCE bliver krypteret sammen
    encrypted = server_box.encrypt(server_s_key,nonce)
    #Den symmetriske key bliver sendt til client 
    client.send(bytes(encrypted))

def encrypt_message(message):
    """Encrypt messages"""
    global server_s_box
    #Kryptere beskeden med den symmetriske key
    encrypted = server_s_box.encrypt(message)
    #Kontrollerer at længden af beskeden stemmer overens med den ukrypteret besked + NONCE + MAC
    assert len(encrypted) == len(message) + server_s_box.NONCE_SIZE + server_s_box.MACBYTES
    #Herefter bliver en NONCE lavet
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    #Beskeden bliver krypteret med en NONCE
    encrypted_s_message = server_s_box.encrypt(message, nonce)
    ctext = encrypted_s_message.ciphertext
    #Kontrollerer at længden på ciphertext passer med message og MAC
    assert len(ctext) == len(message) + server_s_box.MACBYTES
    return(encrypted_s_message)

def decrypt_message(message):
    """Decrypts messages"""
    #Dekrypterer beskeden med den symmetriske nøgle
    plaintext = server_s_box.decrypt(message)
    return plaintext.decode('utf-8')

"""------------ Above this line is changes ------------"""

""" 
Other changes is the broadcast function should no longer be called with bytes.
The function will convert it to bytes.

"""



def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        key_exchange(client)
        print("%s:%s has connected." % client_address)
        client.send(encrypt_message(bytes(str("Greetings from the cave! Now type your name and press enter!"), "utf8")))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = decrypt_message(client.recv(BUFSIZ))
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(encrypt_message(bytes(str(welcome),"utf8")))
    msg = "%s has joined the chat!" % name
    broadcast(msg)
    clients[client] = name

    while True:
        msg = decrypt_message(client.recv(BUFSIZ))
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.send(encrypt_message(bytes("{quit}", "utf8")))
            client.close()
            del clients[client]
            broadcast("%s has left the chat." % name)
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    
    for sock in clients:
        sock.send(encrypt_message(bytes(prefix, 'utf8')+bytes(msg, 'utf8')))

        
clients = {}
addresses = {}


#----Now comes the arguments part----
parser = argparse.ArgumentParser(description='This is the server for the chat.')
parser.add_argument('ip', type=str, nargs='?', default='127.0.0.1',
                    help='the ip you want to bind. (default 127.0.0.1)')

parser.add_argument('-p','--port', type=int, nargs='?', default=33000,
                    help='the port. (default 33000)')  
parser.add_argument('-s','--buff-size', type=int, nargs='?', default=1024,
                    help='the size of the buffer. (default 1024)')
                    
args = parser.parse_args()
HOST=args.ip
PORT=args.port 
BUFSIZ = args.buff_size

ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print(f'[INFO] Server started on {HOST}:{PORT}, buffer size: {BUFSIZ}')
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
