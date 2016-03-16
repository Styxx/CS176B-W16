# Echo server program
import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 6000               # Arbitrary non-privileged port
MAX = 5

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print socket.gethostname()
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr
counter = 0
while 1:
    data = conn.recv(1024)
    print 'received data'
    if not data: break
    conn.sendall(data)
    print 'sent data: ' + data
    counter = counter + 1
    if counter > MAX:
        break
conn.close()