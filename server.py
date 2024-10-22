import socket

# Input IP dan port
IpAddress = input("Masukkan IP Address: ")
portServer = int(input("Masukkan Port Number: "))

# Membuat server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((IpAddress, portServer))  # Buat ngiket si IP sama port biar server bisa nerima pesannya

# Inisialisasi
clients = {}
noClient = {}

print(f"Chatroom server running on {IpAddress}:{portServer}...")

while True:
    data, clientAddress = serverSocket.recvfrom(1024)
    message = data.decode() # Decode ini ngubah pesan dari byte ke string
    noUrut, username, pesan = message.split("|", 2)
    noUrut = int(noUrut)
    
    # Buat client baru
    if clientAddress not in clients:
        clients[clientAddress] = username
        noClient[clientAddress] = -1
        print(f"New client joined: {username} ({clientAddress})")
    
    if noUrut == noClient[clientAddress] + 1:
        noClient[clientAddress] = noUrut  # Update nomor urut terakhir
        
        # Broadcast pesan ke semua client
        for client in clients:
            if client != clientAddress:
                serverSocket.sendto(data, client)
        
        # Kirim ACK ke pengirim dan tampilkan log di server
        ackMessage = f"ACK|{noUrut}"
        serverSocket.sendto(ackMessage.encode(), clientAddress)
        print(f"LOG: Received message from {username} ({clientAddress}): {pesan}")
        print(f"LOG: Sent ACK for message {noUrut} to {clientAddress}")

    else:
        print(f"Received out-of-order packet from {clientAddress}. Expected {noClient[clientAddress] + 1}, but got {noUrut}.")