import socket
import os



class ServerSocketHandler():
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 4444
    SEPARATOR = '<SEPARATOR>'
    BUFFER_SIZE = 4096

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.SERVER_HOST, self.SERVER_PORT))

    def listenForFiles(self):
        self.s.listen(5)
        print(f'[+] Listening on port {self.SERVER_PORT}')
        while True:

            client_socket, addres = self.s.accept()
            print(f'[+] {addres} connected')

            recieved = client_socket.recv(self.BUFFER_SIZE).decode()
            filename, filesize = recieved.split(self.SEPARATOR)
            filename = os.path.join('draws', filename)
            print(f'[+] creating {filename}')
            filesize = int(filesize)

            with open(filename, 'wb') as f:
                bytes_read = client_socket.recv(self.BUFFER_SIZE)
                if not bytes_read:
                    break

                f.write(bytes_read)
            print(f'[+] Done recieving {filename}')

            