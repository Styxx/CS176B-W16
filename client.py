# Echo client program
import socket

HOST = 'styxx-cs176-lab3-2731309'    # The remote host
PORT = 57575# The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall('GET /who/ken/trust.html HTTP/1.1\r\nHost: styxx-cs176-lab3-2731309\r\nAccept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3\r\nAccept: text/html;q=0.9,text/plain\r\n\r\n')
while True:
    data = s.recv(1024)
    if data == "":
        s.close()
        break
    else:
        print 'Received', repr(data)
        s.sendall('More data!')