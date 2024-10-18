import socket

# Input IP dan port
IpAddress = input("Enter server IP (e.g., 127.0.0.1): ")
portServer = int(input("Enter server port (e.g., 12345): "))

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((IpAddress, portServer))

clients = set()

print(f"Chatroom server running on {IpAddress}:{portServer}...")

while True:
  # Menerima pesan dari client
  data, clientAddress = serverSocket.recvfrom(1024)
  print(f"Received data from {clientAddress}: {data.decode()}")

  # Kalau client baru, ditambahin ke set client
  if clientAddress not in clients:
    clients.add(clientAddress)
    print(f"New client joined: {clientAddress}")

  # Kirim pesan ke semua client (kecuali pengirim)
  for client in clients:
    if client != clientAddress:
      serverSocket.sendto(data, client)


