import socket
import threading
import time

# INPUT IP dan PORT SERVER device lain
IpAddress = input("Masukkan IP Adress: ")
portServer = int(input("Masukkan Port Number: "))
clientPort = int(input("Masukkan clientPort: "))
username = input("Masukkan username Anda: ")  # Input username

# Ini bikin pintu buat client (socketnya client)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Buat custom port
clientSocket.bind(('', clientPort))

# Inisialisasi untuk nomor urut dan ACK
noUrut = 0
ackTerima = False
durasiTimeout = 2.0  # Durasi timeout tunggu ack

# Fungsi kirim pesan ke server
def sendMessage():
    global noUrut, ackTerima
    while True:
        data = input("You: ")  # Input pesan dari user (tampilannya 'You')
        message = f"{noUrut}|{username}|{data}"  # Kirim nomor urut dan username ke server
        clientSocket.sendto(message.encode(), (IpAddress, portServer))  # Kirim pesan ke server
        
        # Tunggu ACK
        startTime = time.time()
        while time.time() - startTime < durasiTimeout:
            if ackTerima:
                noUrut += 1  # Naikkan nomor urut jika ACK diterima
                ackTerima = False  # Reset status ACK
                break
        if not ackTerima:
            clientSocket.sendto(message.encode(), (IpAddress, portServer))

# Fungsi untuk menerima pesan dari server
def receiveMessage():
    global ackTerima
    while True:
        try:
            data, addr = clientSocket.recvfrom(1024)
            message = data.decode()

            if message.startswith("ACK"):
                angkaAck = int(message.split("|")[1])
                if angkaAck == noUrut:
                    ackTerima = True
            else:
                # Parsing pesan dari server
                _, sender, chatMessage = message.split("|", 2)

                # Cek apakah pengirimnya adalah user sendiri
                if sender == username:
                    print(f"You: {chatMessage}")
                else:
                    print(f"{sender}: {chatMessage}")  # Jika pengirimnya bukan user, tampilkan username

        except Exception as e:
            print(f"LOG: Error saat menerima pesan: {e}")
            break

# Thread untuk mengirim dan menerima pesan
sendThread = threading.Thread(target=sendMessage)
receiveThread = threading.Thread(target=receiveMessage)

sendThread.start()
receiveThread.start()

sendThread.join()
receiveThread.join()