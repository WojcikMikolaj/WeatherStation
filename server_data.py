import socket


class ServerData:
    port = 4000
    address = '0.0.0.0'
    socket_type_first = socket.AF_INET
    socket_type_second = socket.SOCK_DGRAM
