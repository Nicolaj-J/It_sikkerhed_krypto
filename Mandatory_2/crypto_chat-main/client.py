#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
import argparse
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
"""------------ Below this line is changes ------------"""
import nacl.utils
import nacl.secret
from nacl.public import PrivateKey, Box

title_chat = 'Chatter'


def key_exchange():
    """Handles key exchange with the server"""
    #Laver public og private key
    global client_s_key
    global client_s_box
    #Laver public og private key
    sk_client = PrivateKey.generate()
    pk_client = sk_client.public_key
    #Sender dens public key til serveren.
    client_socket.send(bytes(pk_client))
    #Modtager servers public key
    pk_server = nacl.public.PublicKey(client_socket.recv(BUFSIZ))
    #Mdtager den krypteret symmetriske key
    client_s_key_encrypted = client_socket.recv(BUFSIZ)
    #Laver en box med sin egen private key og serverens public key
    client_box = Box(sk_client, pk_server)
    #Dekrypterer den symmetriske key
    client_s_key = client_box.decrypt(client_s_key_encrypted)
    #Laver en box med den symmetriske key
    client_s_box = nacl.secret.SecretBox(client_s_key)


def encrypt_message(message):
    #Kryptere beskeden med den symmetriske key
    encrypted = client_s_box.encrypt(bytes(str(message),"utf8"))
    #Kontrollerer at længden af beskeden stemmer overens med den ukrypteret besked + NONCE + MAC
    assert len(encrypted) == len(message) + client_s_box.NONCE_SIZE + client_s_box.MACBYTES
    #Herefter bliver en NONCE lavet
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    #Beskeden bliver krypteret med en NONCE
    encrypted_s_message = client_s_box.encrypt(bytes(str(message),"utf8"), nonce)
    ctext = encrypted_s_message.ciphertext
    #Kontrollerer at længden på ciphertext passer med message og MAC
    assert len(ctext) == len(message) + client_s_box.MACBYTES
    return(encrypted_s_message)

def decrypt_message(message):
    #Laver message om til et EncryptetMessage objekt
    message = nacl.utils.EncryptedMessage(message)
    #Dekrypterer beskeden med den symmetriske nøgle
    plaintext = client_s_box.decrypt(message)
    return plaintext.decode('utf-8')

"""------------ Above this line is changes ------------"""

def receive():
    """Handles receiving of messages."""
    global title_chat
    while True:
        try:
            msg = decrypt_message(client_socket.recv(BUFSIZ))
            msg_list.insert(tkinter.END, msg)
            if msg.startswith('Welcome') and title_chat == 'Chatter':
                title_chat += ' ' + msg.split()[1]
                top.title(title_chat)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(encrypt_message((msg))))
    if msg == "{quit}":
        client_socket.close()
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()

top = tkinter.Tk()
top.title(title_chat)

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Username?")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()


entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the arguments part----
parser = argparse.ArgumentParser(description='This is the client for the chat.')
parser.add_argument('ip', type=str, nargs='?', default='127.0.0.1',
                    help='the ip you want to connect to. (default 127.0.0.1)')

parser.add_argument('-p','--port', type=int, nargs='?', default=33000,
                    help='the port. (default 33000)')  
parser.add_argument('-s','--buff-size', type=int, nargs='?', default=1024,
                    help='the size of the buffer. (default 1024)')
                    
args = parser.parse_args()
HOST=args.ip
PORT=args.port 
BUFSIZ = args.buff_size
ADDR = (HOST, PORT)

#----Now comes the sockets part----
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)
print(f'[INFO] Connected to {HOST}:{PORT}, buffer size: {BUFSIZ}')
key_exchange()
receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.
