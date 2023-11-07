import socket
from threading import Thread

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostname(), 55555))

server.listen(2)
print("Server is Running...")

clients = []
currentPlayer = 0

def handle(client, player):
    data = client.recv(1024).decode()
    while True:
        print(f"RECIEVED {player}:: ", data)
        data = client.recv(1024).decode()

while True:
    conn, addr = server.accept()
    print("Connected to ::", addr[0])

    clients.append(conn)

    thread = Thread(target=handle, args=(conn, currentPlayer,))
    thread.daemon = True
    thread.start()
    currentPlayer += 1