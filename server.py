import socket

# Input IP dan port
IpAddress = input("Enter server IP (e.g., 127.0.0.1): ")
portServer = int(input("Enter server port (e.g., 12345): "))

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((IpAddress, portServer))

clients = {}
#variabel untuk simpen nomor urut terakhir dari tiap client
noClient = {}

print(f"Chatroom server running on {IpAddress}:{portServer}...")

while True:
  # Menerima pesan dari client
  data, clientAddress = serverSocket.recvfrom(1024)
  message = data.decode()
  noUrut, pesan = message.split("|", 1)
  noUrut = int(noUrut) #konversi nomor urut ke integer
  
  if clientAddress not in clients:
      clients[clientAddress] = True
      noClient[clientAddress] = -1 #inisialisasi nomor urut menjadi -1
      print(f"New client joined: {clientAddress}")
  
  #cek apakah nomor urut pesan yang diterima sesuai dengan urutan
  if noUrut == noClient[clientAddress] + 1:
      noClient[clientAddress] = noUrut  #update nomor urut terakhir untuk client ini
      
      #tampilkan pesan yang diterima
      print(f"Received data from {clientAddress}: {noUrut}|{pesan}")
      
      #kirim ack ke client
      ackMessage = f"ACK|{noUrut}"
      serverSocket.sendto(ackMessage.encode(), clientAddress)
      print(f"Sent ACK {ackMessage} to {clientAddress}")
      
      #kirim pesan ke semua client lain (broadcast)
      for client in clients:
          if client != clientAddress:
              serverSocket.sendto(data, client)
  else:
      print(f"Received out-of-order packet from {clientAddress}. Expected {noClient[clientAddress] + 1}, but got {noUrut}.")

