import socket

# Fungsi enkripsi menggunakan Caesar Cipher enskripsi
def caesar_encrypt(text, shift):
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            shift_base = ord('a') if char.islower() else ord('A')
            encrypted_text += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            encrypted_text += char
    return encrypted_text

# Fungsi dekripsi menggunakan Caesar Cipher dekripsi
def caesar_decrypt(text, shift):
    decrypted_text = ""
    for char in text:
        if char.isalpha():
            shift_base = ord('a') if char.islower() else ord('A')
            decrypted_text += chr((ord(char) - shift_base - shift) % 26 + shift_base)
        else:
            decrypted_text += char
    return decrypted_text

# Fungsi Caesar Cipher untuk dekripsi pesan
def caesar_cipher_decrypt(message, shift):
    decrypted_message = ""
    for char in message:
        if char.isalpha():  # Hanya mendekripsi huruf alfabet
            shift_base = 65 if char.isupper() else 97
            decrypted_message += chr((ord(char) - shift_base - shift) % 26 + shift_base)
        else:
            decrypted_message += char  # Karakter non-alfabet tidak diubah
    return decrypted_message

# Input IP dan port
IpAddress       = input("Masukkan IP Address    : ")
portServer      = int(input("Masukkan Port Number   : "))
server_password = input("Set server password    : ")

# Kunci shift untuk Caesar Cipher
shift = 11  # Bisa diganti sesuai kebutuhan

# Membuat server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((IpAddress, portServer))

# Inisialisasi
clients = {}
noClient = {}

print(f"Chatroom server running on {IpAddress}:{portServer}...")

while True:
    data, clientAddress = serverSocket.recvfrom(1024)
    message = caesar_decrypt(data.decode(), shift)  # Dekripsi pesan

    #Tambahkan bukti untuk pembuktian bahwa Caesar Cipher berhasil
    print(f"Encrypted message received: {data.decode()}")
    print(f"Decrypted message: {message}")
    # Cek apakah pesan ini adalah autentikasi dalam format "PASSWORD_CHECK|username|password"
    if message.startswith("PASSWORD_CHECK"):
        try:
            _, username, password = message.split("|", 2)
            if password == server_password:
                if clientAddress not in clients:
                    clients[clientAddress] = "Authenticated"
                    noClient[clientAddress] = -1
                    print(f"Client authenticated successfully from {clientAddress}")
                serverSocket.sendto(caesar_encrypt("AUTH_SUCCESS", shift).encode(), clientAddress)  # Kirim respon terenkripsi
            else:
                print(f"Failed authentication attempt from {clientAddress}.")
                serverSocket.sendto(caesar_encrypt("AUTH_FAILED", shift).encode(), clientAddress)  # Kirim respon terenkripsi
            continue
        except ValueError:
            print("Pesan autentikasi tidak dalam format yang sesuai.")
            continue

    if clientAddress not in clients or clients[clientAddress] != "Authenticated":
        print(f"Failed authentication attempt from {clientAddress}.")
        continue

    # Proses pesan chat sesuai format yang sudah ada
    try:
        noUrut, username, pesan = message.split("|", 2)
        noUrut = int(noUrut)

        if noUrut == noClient[clientAddress] + 1:
            noClient[clientAddress] = noUrut

            # Broadcast pesan ke semua client terenkripsi
            encrypted_message = caesar_encrypt(message, shift)
            for client in clients:
                if client != clientAddress:
                    serverSocket.sendto(encrypted_message.encode(), client)

            # Kirim ACK ke pengirim terenkripsi dan tampilkan log di server
            ackMessage = f"ACK|{noUrut}"
            serverSocket.sendto(caesar_encrypt(ackMessage, shift).encode(), clientAddress)
            print(f"LOG: Received message from {username} ({clientAddress}): {pesan}")
            print(f"LOG: Sent ACK for message {noUrut} to {clientAddress}")

        else:
            print(f"Received out-of-order packet from {clientAddress}. Expected {noClient[clientAddress] + 1}, but got {noUrut}.")

    except ValueError:
        print("LOG: Pesan tidak dalam format yang sesuai.")