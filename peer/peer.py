import requests
import socket
import threading
from PIL import Image


def is_port_busy(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.bind(("localhost", port))
        sock.close()
        return False
    except socket.error:
        return True


def file_receiver(my_ip, target_ip, filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_and_ip = (target_ip, 10000)
    sock.connect(port_and_ip)
    empty_port = 1
    for i in range(10001, 10011):
        if not is_port_busy(empty_port):
            empty_port = i
    if empty_port == 1:
        print("you dont have any free legal port!!")
        return
    message = my_ip + ':' + str(empty_port) + ':' + filename
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((my_ip, empty_port))
    sock.sendall(message.encode())
    chunks = []
    while True:
        chunk, addr = udp_socket.recvfrom(1024)
        if not chunk:
            break
        chunks.append(chunk)

    # Combine the received chunks into a single byte string
    data = b''.join(chunks)

    # Write the data to a file
    with open('./files/' + filename, 'wb') as f:
        f.write(data)

    # Close the socket
    udp_socket.close()
    sock.close()


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


tcp_handshake_port = 10000
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
init_url = 'http://127.1.1.2:8080/init'
get_usernames = 'http://127.1.1.2:8080/getAll'
get_ip = 'http://127.1.1.2:8080/getIp?username='
threading.Thread(target=listener, args=(ip_address, tcp_handshake_port)).start()
print("Welcome to this p2p app")
while True:
    inp = input('choose your action:\n1.init \n2.get usernames\n3.get specific ip\n4.request for connection\ninput:')
    if inp == '1':
        username = input("Enter a username:")
        data = {
            "username": username,
            "ip": ip_address
        }
        response = requests.post(init_url, json=data)
        print('HTTP Server Response:', response.text)
    elif inp == '2':
        response = requests.get(get_usernames)
        print('HTTP Server Response:', response.text)
    elif inp == '3':
        target_ip = input("Enter Target Ip:")
        response = requests.get(get_ip + target_ip)
        print('HTTP Server Response:', response.text)
    elif inp == '4':
        target_ip = input('Enter your target ip:')
        filename = input('Enter filename:')
        threading.Thread(target=file_receiver, args=(ip_address, target_ip, filename)).start()

    else:
        print("wrong Command!!!")
