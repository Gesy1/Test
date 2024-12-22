from tkinter import *
import socket
import cv2
import pickle
import struct
from PIL import Image, ImageTk
import threading
import queue


def Connection():
    host1 = input_2.get()
    port1 = int(input_3.get())

    global Mon_client
    Mon_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    address = (host1, port1)

    try:
        Mon_client.connect(address)
        confirmation = Label(boite2, text="Connexion réussie", fg="green")
        confirmation.pack()

        # Créez un thread pour recevoir des vidéos
        video_thread = threading.Thread(target=receive_video)
        video_thread.daemon = True  # Permet au programme de se fermer même si le thread tourne
        video_thread.start()  
    except Exception as e:
        echec = Label(boite2, text=f"Connexion échouée: {e}", fg="red")
        echec.pack()


def start_video():
    global video_source
    video_source = cv2.VideoCapture(0)
    update_video()


def update_video():
    global video_source, user_video_label, user_photo

    ret, frame = video_source.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = img.resize((160, 120))
        user_photo = ImageTk.PhotoImage(img)
        user_video_label.config(image=user_photo)

    user_video_label.after(10, update_video)


def receive_video():
    global client_photo, client_video_label, data_queue
    data = b""
    payload_size = struct.calcsize("Q")

    while True:
        while len(data) < payload_size:
            packet = Mon_client.recv(4 * 1024)
            if not packet:
                break
            data += packet
        
        if len(data) < payload_size:
            continue
        
        packet_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packet_msg_size)[0]

        while len(data) < msg_size:
            data += Mon_client.recv(4 * 1024)
        
        frame_data = data[:msg_size]
        data = data[msg_size:]

        try:
            frame = pickle.loads(frame_data)
            if frame is None:
                continue
            
            # Mettez l'image dans la queue pour le traitement
            data_queue.put(frame)
        except Exception as e:
            print(f"Erreur lors de la réception de la vidéo : {e}")
            break


def update_client_video():
    global client_photo, client_video_label

    # Vérifiez s'il y a une nouvelle image dans la queue
    while not data_queue.empty():
        frame = data_queue.get()
        if frame is None:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = img.resize((640, 480))
        client_photo = ImageTk.PhotoImage(img)
        client_video_label.config(image=client_photo)

    client_video_label.after(10, update_client_video)


# Initialisation
data_queue = queue.Queue()  # Créer une queue pour stocker les images

Fenetre = Tk()
Fenetre.title("Webcam")
Fenetre.geometry("40x40")
Fenetre.minsize(1200, 720)
Fenetre.config(bg="azure3")

boite1 = Frame(Fenetre, bd=1, bg="#76EEC6")
boite1.pack(fill=X)

boite2 = Frame(Fenetre, bd=1)
boite2.pack()

boite3 = Frame(Fenetre, bg="#d1e7dd", bd=2, relief="solid")
boite3.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

boite4 = Frame(Fenetre, bg="#f8d7da", bd=2, relief="solid")
boite4.pack(side=RIGHT, fill=Y, padx=10, pady=10)

text_titre = Label(boite1, text="Welcome to my app", font=("arial", 20), bg="#76EEC6")
text_titre.pack()

text_1 = Label(boite2, text="Entre l'addresse du serveur a pour se connecter", font=("arial", 12))
text_1.pack()

text_2 = Label(boite2, text="Hostname", font=("Arial", 12))
text_2.pack()
input_2 = Entry(boite2, font=("Arial", 12), bg="gray")
input_2.pack()

text_3 = Label(boite2, text="port", font=("Arial", 12))
text_3.pack()
input_3 = Entry(boite2, font=("Arial", 12), bg="gray")
input_3.pack()

button1 = Button(boite2, text="submit", font=("Arial", 10), bg="gray", command=Connection)
button1.pack()
button2 = Button(boite2, text="afficher le mien", font=("Arial", 10), bg="gray", command=lambda: threading.Thread(target=start_video).start())
button2.pack()

client_label = Label(boite3, text="Vidéo Client", bg="#d1e7dd", font=("Arial", 24))
client_label.pack(pady=10)

user_label = Label(boite4, text="Votre Vidéo", bg="#f8d7da", font=("Arial", 20))
user_label.pack(pady=10)

user_video_label = Label(boite4, bg="#f8d7da")
user_video_label.pack()

client_video_label = Label(boite3, bg="#d1e7dd")
client_video_label.pack()

# Commencez la mise à jour de la vidéo du client
update_client_video()  # Initialiser l'update pour le client video

Fenetre.mainloop()

video_source.release()
cv2.destroyAllWindows()