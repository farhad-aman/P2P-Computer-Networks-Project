import requests
import socket
import threading
from PIL import Image


def receiver(host, target_ip, filename):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (target_ip, 8080)
    soc.connect(address)
    message = host + ':' + filename
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, 8081))
    soc.sendall(message.encode())
    chunks = []
    while True:
        chunk, addr = udp_socket.recvfrom(1024)
        if not chunk:
            break
        chunks.append(chunk)
    file = b''.join(chunks)
    with open('./files/' + filename, 'wb') as f:
        f.write(file)
    udp_socket.close()
    soc.close()


def file_sender(dest_ip, dest_port, dest_filename):
    HOST = dest_ip
    PORT = int(dest_port)
    BUFFER_SIZE = 1024

    # with open('./files/' + dest_filename, 'rb') as f:
    #     data = f.read()
    data = Image.open('./files/' + dest_filename)
    data = data.tobytes()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(0, len(data), BUFFER_SIZE):
        chunk = data[i:i + BUFFER_SIZE]
        sock.sendto(chunk, (HOST, PORT))

    sock.sendto(b'', (HOST, PORT))

    sock.close()


def listener(ip_address, tcp_handshake_port):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_address = (ip_address, tcp_handshake_port)
        sock.bind(local_address)
        sock.listen()
        client_sock, client_address = sock.accept()
        data = client_sock.recv(1024).decode('utf-8')
        data = data.split(':')
        dest_ip = data[0]
        dest_port = data[1]
        dest_filename = data[2]
        # ip, port, filename = data
        acceptance = False
        while True:
            inp = input(
                'a system with ip ' + client_address + 'wants to connect you and receive "' + dest_filename + '", do '
                                                                                                              'you'
                                                                                                              'wanna'
                                                                                                              'accept'
                                                                                                              '?\n1'
                                                                                                              '.yes'
                                                                                                              '\n2.no'
                                                                                                              '\ninput:')
            if inp == '1':
                acceptance = True
                break
            elif inp == '2':
                break
            else:
                print('invalid input!')
        if acceptance:
            sock.sendall(b"Done")
            threading.Thread(target=file_sender, args=(dest_ip, dest_port, dest_filename)).start()
        else:
            sock.sendall(b"None")
        sock.close()


if __name__ == "__main__":
    server_address = "127.0.0.1"
    server_port = "80"
    port = 8080
    host = socket.gethostbyname(socket.gethostname())
    register = server_address + ":" + server_port + "/register"
    get_all = server_address + ":" + server_port + "/get-all"
    get = server_address + ":" + server_port + "getIp?username="
    threading.Thread(target=listener, args=(host, port)).start()
    print("Peer Started")
    while True:
        option = input('1: init \n2: get all\n3: get\n4: request for connection\ninput:')
        if option == '1':
            username = input("Username:")
            data = {
                "username": username,
                "ip": host
            }
            response = requests.post(register, json=data)
            print('Response:', response.text)
        elif option == '2':
            response = requests.get(get_all)
            print('Response:', response.text)
        elif option == '3':
            username = input("Target Username:")
            response = requests.get(get + username)
            print('Response:', response.text)
        elif option == '4':
            target_ip = input('Target IP:')
            filename = input('Filename:')
            threading.Thread(target=receiver, args=(host, target_ip, filename)).start()
        else:
            print("Invalid Command")