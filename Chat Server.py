import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime

HOST = 'localhost'
PORT = 12345

clients = {}  # socket: username
banned_users = set()

def broadcast(message, sender_socket=None):
    for client_socket in list(clients):
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except:
                disconnect_client(client_socket)

def handle_client(client_socket, addr, chat_area, user_listbox):
    try:
        username = client_socket.recv(1024).decode()
        if username in banned_users:
            client_socket.send("You are banned.".encode())
            client_socket.close()
            return

        clients[client_socket] = username
        update_user_list(user_listbox)
        chat_area.insert(tk.END, f"{username} connected\n")
        broadcast(f"{username} has joined the chat.", client_socket)

        while True:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            timestamped_msg = f"{msg}"
            chat_area.insert(tk.END, timestamped_msg + "\n")
            broadcast(timestamped_msg, client_socket)
    except:
        pass
    finally:
        disconnect_client(client_socket)
        update_user_list(user_listbox)
        chat_area.insert(tk.END, f"{clients.get(client_socket, 'Unknown')} disconnected\n")

def disconnect_client(client_socket):
    username = clients.pop(client_socket, None)
    try:
        client_socket.close()
    except:
        pass
    broadcast(f"{username} has left the chat.")

def ban_user(user_listbox):
    selected = user_listbox.curselection()
    if selected:
        username = user_listbox.get(selected)
        banned_users.add(username)
        for client_socket, user in list(clients.items()):
            if user == username:
                disconnect_client(client_socket)
                break
        update_user_list(user_listbox)

def update_user_list(user_listbox):
    user_listbox.delete(0, tk.END)
    for user in clients.values():
        user_listbox.insert(tk.END, user)

def start_server(chat_area, user_listbox):
    def run():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        chat_area.insert(tk.END, f"Server started on {HOST}:{PORT}\n")

        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr, chat_area, user_listbox), daemon=True).start()

    threading.Thread(target=run, daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("Chat Server Admin Panel")
root.geometry("700x400")

# Chat display
chat_area = scrolledtext.ScrolledText(root, width=60, height=20, state='normal')
chat_area.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Sidebar with user list and controls
sidebar = tk.Frame(root)
sidebar.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

user_listbox = tk.Listbox(sidebar, height=15)
user_listbox.pack(pady=5, fill=tk.BOTH)

disconnect_btn = tk.Button(sidebar, text="Disconnect", command=lambda: kick_selected_user(user_listbox))
disconnect_btn.pack(pady=5, fill=tk.X)

ban_btn = tk.Button(sidebar, text="Ban User", command=lambda: ban_user(user_listbox))
ban_btn.pack(pady=5, fill=tk.X)

start_btn = tk.Button(sidebar, text="Start Server", command=lambda: start_server(chat_area, user_listbox))
start_btn.pack(pady=5, fill=tk.X)

def kick_selected_user(user_listbox):
    selected = user_listbox.curselection()
    if selected:
        username = user_listbox.get(selected)
        for client_socket, user in list(clients.items()):
            if user == username:
                disconnect_client(client_socket)
                update_user_list(user_listbox)
                chat_area.insert(tk.END, f"{username} was disconnected\n")
                break

root.mainloop()