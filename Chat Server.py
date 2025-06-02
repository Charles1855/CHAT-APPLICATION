import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = 'localhost'
PORT = 12345
CHAT_HISTORY_FILE = 'chat_history.txt'

clients = []


def save_message_to_file(message):
#Append message to chat history file.
    with open(CHAT_HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(message + "\n")


def send_chat_history(client_socket):
 #Send previous chat messages to a newly connected client.
    try:
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                client_socket.send(line.strip().encode() + b'\n')
    except FileNotFoundError:
        pass  # No history exists yet


def broadcast(message, sender_socket):
    #Send message to all connected clients except the sender.
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                clients.remove(client)


def handle_client(client_socket, addr, chat_area):
    #Manage communication with a single client.
    send_chat_history(client_socket)  # Send chat history on connection

    while True:
        try:
            msg = client_socket.recv(1024)
            if not msg:
                break
            decoded_msg = msg.decode()
            full_msg = f"{addr}: {decoded_msg}"
            chat_area.insert(tk.END, full_msg + "\n")
            save_message_to_file(full_msg)
            broadcast(msg, client_socket)
        except:
            break

    client_socket.close()
    if client_socket in clients:
        clients.remove(client_socket)
    disconnect_msg = f"{addr} disconnected"
    chat_area.insert(tk.END, disconnect_msg + "\n")
    save_message_to_file(disconnect_msg)


def start_server(chat_area):
    def run():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        chat_area.insert(tk.END, f"Server started on {HOST}:{PORT}\n")
        save_message_to_file(f"Server started on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            clients.append(client_socket)
            connection_msg = f"New connection: {addr}"
            chat_area.insert(tk.END, connection_msg + "\n")
            save_message_to_file(connection_msg)
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