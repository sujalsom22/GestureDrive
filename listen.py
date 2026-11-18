import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 4210))
print("listening on 4210")
while True:
    print(s.recvfrom(16)[0])
