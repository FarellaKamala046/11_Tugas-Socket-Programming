#CLIENT

import socket
import threading

#INPUT IP dan PORT SERVER device lain
IpAddress = input("Masukkan IP Adress: ")
portServer = int(input("Masukkan Port Number: "))
clientPort = int(input("Masukkan clientPort: "))

#ini bikin pintu buat client (socketnya client)
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#buat custom port. kalau gapake bind, otomatis dikirim dari sananya
clientSocket.bind(('', clientPort))

#fungsi kirim pesan ke server
def sendMessage():
    while True:
        data = input("You: ") #input dari user
        clientSocket.sendto(data.encode(), (IpAddress,portServer)) #kirim pesan ke server
#fungsi untuk menerima pesan dari server
def receiveMessage():
    while True:
        try:
            data, addr = clientSocket.recvfrom(1024)
            print(f"Pesan dari server: {data.decode()} from {addr}")
        except Exception as e:
            print(f"Error saat menerima pesan: {e}")
            break


#thread untuk bikin jalur di program ada yang kirim ada yang terima
sendThread = threading.Thread(target = sendMessage)
receiveThread = threading.Thread(target = receiveMessage)

sendThread.start() #ini threat buat kirim
receiveThread.start() #ini threat buat terima

sendThread.join() #ini menunggu thread kirimnya selesai
receiveThread.join() #ini tunggu thread kirim selesai