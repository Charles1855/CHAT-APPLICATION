# chat_server_gui.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = 'localhost'
PORT = 12345

clients = []

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                clients.remove(client)

def handle_client(client_socket, addr, chat_area):
    while True:
        try:
            msg = client_socket.recv(1024)
            if not msg:
                break
            chat_area.insert(tk.END, f"{addr}: {msg.decode()}\n")
            broadcast(msg, client_socket)
        except:
            break
    client_socket.close()
    clients.remove(client_socket)
    chat_area.insert(tk.END, f"{addr} disconnected\n")

def start_server(chat_area):
    def run():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        chat_area.insert(tk.END, f"Server started on {HOST}:{PORT}\n")
        while True:
            client_socket, addr = server_socket.accept()
            clients.append(client_socket)
            chat_area.insert(tk.END, f"New connection: {addr}\n")
            threading.Thread(target=handle_client, args=(client_socket, addr, chat_area), daemon=True).start()

    threading.Thread(target=run, daemon=True).start()

# GUI Setup
root = tk.Tk()
root.title("Chat Server")

chat_area = scrolledtext.ScrolledText(root, width=60, height=20, state='normal')
chat_area.pack(padx=10, pady=10)

start_btn = tk.Button(root, text="Start Server", command=lambda: start_server(chat_area))
start_btn.pack(pady=5)

root.mainloop()