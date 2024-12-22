import socket
import cv2
import pickle
import struct


Mon_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 6600

address = (host, port)

Mon_serveur.bind(address)
print(f"en ecoute sur {address}")

Mon_serveur.listen(1)



while True:
    client_socket, client_addr = Mon_serveur.accept()
    print(client_addr)
    
    if client_socket:
        video = cv2.VideoCapture(0)
        while(video.isOpened()):
            img, frame = video.read()
            a = pickle.dumps(frame)
            message = struct.pack("Q",len(a))+a
            client_socket.sendall(message)
            cv2.imshow('Serveur video', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                client_socket.close()