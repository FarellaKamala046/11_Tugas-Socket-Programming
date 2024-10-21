#CLIENT

import socket
import threading
import time

#INPUT IP dan PORT SERVER device lain
IpAddress = input("Masukkan IP Address: ")
portServer = int(input("Masukkan Port Number: "))
clientPort = int(input("Masukkan clientPort: "))

#ini bikin pintu buat client (socketnya client)
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#buat custom port. kalau gapake bind, otomatis dikirim dari sananya
clientSocket.bind(('', clientPort))

#inisialiasi untuk nomor urut (ini untuk mengurutkan paket yang mungkin aja ga sesuai urutan) dan ACK 
noUrut = 0
ackTerima = False
durasiTimeout = 2.0 #Durasi timeout tunggu ack, kalau gaada bakal dikirim ulang


#fungsi kirim pesan ke server
def sendMessage():
    global noUrut, ackTerima
    while True:
        data = input("You: ") #input dari user
        message = f"{noUrut}|{data}" #tambahkan nomor urut
        print(f"LOG: Mengirim pesan dengan nomor urut {noUrut}")
        clientSocket.sendto(message.encode(), (IpAddress,portServer)) #kirim pesan ke server
        print(f"Pesan {data} dengan nomor urut {noUrut} dikirim")
            
        #Tunggu ACK apakah sudah dikirim atau blm
        startTime = time.time()
        while time.time() - startTime < durasiTimeout:
            if ackTerima:
                print (f"LOG: ACK diterima untuk nomor urut {noUrut}")
                noUrut += 1 #No urut dinaikkin kalau ack diterima
                ackTerima = False #Reset status ACK
                print(f"LOG: Nomor urut dinaikkan menjadi {noUrut}")
                break
        if not ackTerima:
            print(f"LOG Timeout terjadi, ACK tidak diterima, mengirim ulang pesan dengan nomor urut {noUrut}")
            clientSocket.sendto(message.encode(), (IpAddress, portServer))
        else:
            print(f"LOG: Pesan dengan nomor urut {noUrut - 1} berhasil dikirim dan diakui.")
            break #kalau ACK diterima, keluar dari loop pengirim
            
#fungsi untuk menerima pesan dari server
def receiveMessage():
    global ackTerima
    while True:
        try:
            data, addr = clientSocket.recvfrom(1024)
            message = data.decode()
            print(f"LOG: Menerima pesan: {message} dari {addr}")
            #cek apakah pesannya itu ACK
            if message.startswith("ACK"):
                angkaAck = int(message.split("|")[1])
                print(f"LOG: ACK diterima dengan nomor {angkaAck}")
                if angkaAck == noUrut:
                    ackTerima = True
                    print(f"LOG: ACK diterima untuk nomor urut {angkaAck}")
                else:
                    print(f"LOG: ACK salah, diabaikan. Diterima: {angkaAck}, Diharapkan: {noUrut - 1}")
            else:
                print(f"Pesan dari server: {message}")

        except Exception as e:
            print(f"LOG: Error saat menerima pesan: {e}")
            break


#thread untuk bikin jalur di program ada yang kirim ada yang terima
sendThread = threading.Thread(target = sendMessage)
receiveThread = threading.Thread(target = receiveMessage)

sendThread.start() #ini threat buat kirim
receiveThread.start() #ini threat buat terima

sendThread.join() #ini menunggu thread kirimnya selesai
receiveThread.join() #ini tunggu thread kirim selesai