import nacl.utils
import nacl.secret
from nacl.public import PrivateKey, Box

#Step 1. Serveren laver den symmetriske key ved startup.
server_s_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

#Step 2. Client laver public og private key
sk_client = PrivateKey.generate()
pk_client = sk_client.public_key


#Step 3. Client forbinder til serveren og sender public key.
#Serveren laver public og private key
sk_server = PrivateKey.generate()
pk_server = sk_server.public_key
print(sk_server, pk_client)
server_box = Box(sk_server, pk_client)
#Serveren sender dens symmetriske key. 


#Step 4. Server sender dens public key tilbage
print(server_s_key)
server_s_box = nacl.secret.SecretBox(server_s_key)
encrypted = server_box.encrypt(server_s_key)
nonce = nacl.utils.random(Box.NONCE_SIZE)
encrypted = server_box.encrypt(server_s_key,nonce)


#Step 5. Client dekryptere den symmetriske key
client_box = Box(sk_client, pk_server)
client_s_key = client_box.decrypt(encrypted)
print(client_s_key)


#Step 6. Client sends a message
client_s_box = nacl.secret.SecretBox(client_s_key)
message = b"hej"
encrypted = client_s_box.encrypt(message)
print("encrypted: ",len(encrypted))
print("message: ",len(message))
print("Nonce: ",client_s_box.NONCE_SIZE)
print("MACBYTES: ",client_s_box.MACBYTES)
assert len(encrypted) == len(message) + client_s_box.NONCE_SIZE + client_s_box.MACBYTES
nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
encrypted_s_message = client_s_box.encrypt(message, nonce)
ctext = encrypted.ciphertext
print(ctext)
print(type(ctext))

#Step 7. Server broadcast the message to all clients


#Step 8. Clients decrypts the broadcast
ctext = b'h\x0e1\xbf\x87\xa4\x90{\x14\xe8\x10\xe8_z\xbch\xb0V\x15\xfa\xdf\x91P#\x01\xdb\xd2\x03fJP\x01'
plaintext = client_s_box.decrypt(encrypted)
print(plaintext.decode('utf-8'))



