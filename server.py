import socket

# Input IP dan port
IpAddress       = input("Masukkan IP Address    : ")
portServer      = int(input("Masukkan Port Number   : "))
server_password = input("Set Server Password    : ")

# Membuat server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((IpAddress, portServer))  # Buat ngiket si IP sama port biar server bisa nerima pesannya

# Inisialisasi
clients = {}
noClient = {}

print(f"Chatroom server running on {IpAddress}:{portServer}...")

# Fungsi untuk mengeluarkan client dari chatroom
def exit_client(clientAddress):
    if clientAddress in clients:
        print(f"Client {clientAddress} keluar dari chatroom.")
        del clients[clientAddress]
        del noClient[clientAddress]

# Tambahkan pengecekan di dalam loop utama server untuk mendeteksi perintah exit
while True:
    data, clientAddress = serverSocket.recvfrom(1024)
    message = data.decode()

    # Cek apakah pesan ini adalah perintah exit
    if message.endswith("exit"):
        exit_client(clientAddress)
        continue

    # Cek apakah pesan ini adalah autentikasi dalam format "PASSWORD_CHECK|username|password"
    if message.startswith("PASSWORD_CHECK"):
        try:
            _, username, password = message.split("|", 2)
            # Bandingkan password yang dikirim client dengan server_password
            if password == server_password:
                if clientAddress not in clients:
                    clients[clientAddress] = "Authenticated"  # Set status client menjadi authenticated
                    noClient[clientAddress] = -1
                    print(f"Client authenticated successfully from {clientAddress}")
                serverSocket.sendto("AUTH_SUCCESS".encode(), clientAddress)
            else:
                print(f"Failed authentication attempt from {clientAddress}.")
                serverSocket.sendto("AUTH_FAILED".encode(), clientAddress)
            continue  # Lanjutkan ke iterasi berikutnya
        except ValueError:
            print("LOG: Pesan autentikasi tidak dalam format yang sesuai.")
            continue

    # Jika bukan pesan autentikasi, lanjutkan ke proses pesan chat
    if clientAddress not in clients or clients[clientAddress] != "Authenticated":
        print(f"Failed authentication attempt from {clientAddress}.")
        continue

    # Proses pesan chat sesuai format yang sudah ada
    try:
        noUrut, username, pesan = message.split("|", 2)
        noUrut = int(noUrut)

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

    except ValueError:
        print("LOG: Pesan tidak dalam format yang sesuai.")