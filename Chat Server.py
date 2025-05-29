import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = 'localhost'
PORT = 12345

clients = {}  # client_socket -> username

def broadcast(message, sender_socket=None):
    for client in list(clients):
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                client.close()
                clients.pop(client, None)

def handle_client(client_socket, addr, chat_area):
    try:
        username = client_socket.recv(1024).decode()
        clients[client_socket] = username
        chat_area.insert(tk.END, f"{username} connected from {addr}\n")
        broadcast(f"{username} has joined the chat.")

        while True:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break

            if msg.startswith("TYPING_START:") or msg.startswith("TYPING_STOP:"):
                broadcast(msg, client_socket)
            else:
                full_msg = f"{username}: {msg}"
                chat_area.insert(tk.END, full_msg + '\n')
                broadcast(full_msg, client_socket)
    except:
        pass
    finally:
        username = clients.get(client_socket, "Unknown")
        chat_area.insert(tk.END, f"{username} disconnected\n")
        broadcast(f"{username} has left the chat.")
        clients.pop(client_socket, None)
        client_socket.close()

def start_server(chat_area):
    def run():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        chat_area.insert(tk.END, f"Server started on {HOST}:{PORT}\n")
        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr, chat_area), daemon=True).start()

    threading.Thread(target=run, daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("Chat Server")

chat_area = scrolledtext.ScrolledText(root, width=60, height=20)
chat_area.pack(padx=10, pady=10)

start_button = tk.Button(root, text="Start Server", command=lambda: start_server(chat_area))
start_button.pack(pady=5)

root.mainloop()