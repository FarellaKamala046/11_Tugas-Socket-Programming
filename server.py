import socket

# Input IP dan port
IpAddress = input("Enter server IP (e.g., 127.0.0.1): ")
portServer = int(input("Enter server port (e.g., 12345): "))

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((IpAddress, portServer))

clients = {}
noClient = {}

print(f"Chatroom server running on {IpAddress}:{portServer}...")

while True:
    data, clientAddress = serverSocket.recvfrom(1024)
    message = data.decode()
    noUrut, username, pesan = message.split("|", 2)
    noUrut = int(noUrut)
    
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
