import socket
import threading
import time
import csv
import os

ascii_art = """
__        __   _                            _        
\ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___  
 \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \ 
  \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
  _\_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/ 
 / ___| |__   __ _| |_|  _ \ ___   ___  _ __ ___ | | 
| |   | '_ \ / _` | __| |_) / _ \ / _ \| '_ ` _ \| | 
| |___| | | | (_| | |_|  _ < (_) | (_) | | | | | |_| 
 \____|_| |_|\__,_|\__|_| \_\___/ \___/|_| |_| |_(_) 

"""

# Fungsi untuk memuat data pengguna dari file CSV
def load_users(filename='users.csv'):
    users = {}
    if os.path.exists(filename):
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                username, password = row
                users[username] = password
    return users

# Fungsi untuk menyimpan pengguna baru ke file CSV
def save_user(username, password, filename='users.csv'):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, password])

# Fungsi untuk login
def login(users):
    while True:
        username = input("Masukkan username: ")
        password = input("Masukkan password: ")
        if username in users and users[username] == password:
            print("Login berhasil!")
            print(ascii_art)
            return username
        else:
            print("Username atau password salah. Coba lagi.")

# Fungsi untuk registrasi
def register(users):
    while True:
        username = input("Masukkan username baru: ")
        if username in users:
            print("Username sudah terdaftar. Coba username lain.")
        else:
            password = input("Masukkan password baru: ")
            save_user(username, password)
            print("Registrasi berhasil!")
            return username

# INPUT IP dan PORT SERVER device lain
IpAddress = input("Masukkan IP Address: ")
portServer = int(input("Masukkan Port Number: "))
clientPort = int(input("Masukkan clientPort: "))

# Ini bikin pintu buat client (socketnya client)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Buat custom port
clientSocket.bind(('0.0.0.0', clientPort))  # Bind ke semua alamat

# Memuat pengguna dari file
users = load_users()

# Memilih antara login atau registrasi
while True:
    action = input("Apa yang kamu mau?\n1. Login\n2. Register\n\nMasukkan angka: ")
    if action == '1':
        username = login(users)
        break
    elif action == '2':
        username = register(users)
        break
    else:
        print("Pilihan tidak valid. Silakan pilih 1 atau 2.")

# Kirim password server untuk autentikasi
server_password = input("Masukkan password server: ")
message = f"PASSWORD_CHECK|{username}|{server_password}"
clientSocket.sendto(message.encode(), (IpAddress, portServer))

# Inisialisasi untuk nomor urut dan ACK
noUrut = 0
ackTerima = False
durasiTimeout = 2.0  # Durasi timeout tunggu ack
authenticated = False  # Flag untuk menandakan apakah sudah terautentikasi

# Terima respon dari server untuk autentikasi
response, addr = clientSocket.recvfrom(1024)
if response.decode() == "AUTH_SUCCESS":
    print("Password server benar. Selamat datang di chatroom!")
    authenticated = True  # Set status autentikasi
else:
    print("Password server salah. Anda tidak dapat masuk ke chatroom.")
    exit()  # Keluar dari program jika autentikasi gagal

# Fungsi kirim pesan ke server
def sendMessage():
    global noUrut, ackTerima, authenticated
    while True:
        if authenticated:  # Hanya kirim pesan jika sudah terautentikasi
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
    while not authenticated:  # Tunggu sampai terautentikasi
        time.sleep(0.5)

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

# Thread untuk mengirim dan menerima pesan (akan diaktifkan setelah autentikasi berhasil)
sendThread = threading.Thread(target=sendMessage)
receiveThread = threading.Thread(target=receiveMessage)

# Mulai thread pengiriman dan penerimaan pesan setelah autentikasi berhasil
sendThread.start()
receiveThread.start()

sendThread.join()
receiveThread.join()