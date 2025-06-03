import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

HOST = 'localhost'
PORT = 12345

clients = {}  # socket -> username
server_socket = None
server_running = False

def broadcast(message, sender_socket=None):
    for client, name in list(clients.items()):
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                client.close()
                del clients[client]

def handle_client(client_socket, addr, chat_area, user_listbox):
    try:
        username = client_socket.recv(1024).decode()
        clients[client_socket] = username
        update_user_list(user_listbox)
        broadcast(f"{username} joined the chat.", client_socket)
        chat_area.insert(tk.END, f"{username} connected.\n")

        while True:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            if msg == "_typing_":
                broadcast(f"{username} is typing...", client_socket)
                continue
            broadcast(msg, client_socket)
            chat_area.insert(tk.END, f"{msg}\n")
    except:
        pass
    finally:
        if client_socket in clients:
            name = clients[client_socket]
            broadcast(f"{name} left the chat.")
            chat_area.insert(tk.END, f"{name} disconnected.\n")
            del clients[client_socket]
            update_user_list(user_listbox)
            client_socket.close()

def update_user_list(user_listbox):
    user_listbox.delete(0, tk.END)
    for name in clients.values():
        user_listbox.insert(tk.END, name)

def start_server(chat_area, user_listbox, start_btn, stop_btn):
    def run():
        global server_socket, server_running
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        server_running = True
        chat_area.insert(tk.END, f"Server started on {HOST}:{PORT}\n")
        while server_running:
            try:
                client_socket, addr = server_socket.accept()
                threading.Thread(target=handle_client, args=(client_socket, addr, chat_area, user_listbox), daemon=True).start()
            except OSError:
                break
    threading.Thread(target=run, daemon=True).start()
    start_btn.config(state='disabled')
    stop_btn.config(state='normal')

def stop_server(chat_area, start_btn, stop_btn):
    global server_socket, server_running
    server_running = False
    for client in list(clients.keys()):
        try:
            client.send("Server is shutting down.".encode())
            client.close()
        except:
            pass
    clients.clear()
    update_user_list(user_listbox)
    if server_socket:
        server_socket.close()
    chat_area.insert(tk.END, "Server stopped.\n")
    start_btn.config(state='normal')
    stop_btn.config(state='disabled')

def disconnect_user(user_listbox, chat_area):
    try:
        selected = user_listbox.get(user_listbox.curselection())
        for sock, name in list(clients.items()):
            if name == selected:
                sock.send("You have been disconnected by the server.".encode())
                sock.close()
                del clients[sock]
                update_user_list(user_listbox)
                broadcast(f"{name} was disconnected by the server.")
                chat_area.insert(tk.END, f"{name} was disconnected.\n")
                break
    except:
        messagebox.showerror("Error", "Please select a user to disconnect.")

# GUI
root = tk.Tk()
root.title("Chat Server")
root.geometry("700x500")
root.config(bg="#fff0f5")

chat_area = scrolledtext.ScrolledText(root, width=70, height=20, state='normal', font=("Segoe UI", 10))
chat_area.pack(padx=10, pady=10)

user_listbox = tk.Listbox(root, width=25)
user_listbox.pack(side=tk.LEFT, padx=(10, 0), pady=(0, 10), anchor='n')

btn_frame = tk.Frame(root, bg="#fff0f5")
btn_frame.pack(side=tk.RIGHT, padx=10, pady=10)

start_btn = tk.Button(btn_frame, text="Start Server", bg="#20b2aa", fg="white", width=15,
                      command=lambda: start_server(chat_area, user_listbox, start_btn, stop_btn))
start_btn.pack(pady=5)

stop_btn = tk.Button(btn_frame, text="Stop Server", bg="#ff4500", fg="white", width=15,
                     command=lambda: stop_server(chat_area, start_btn, stop_btn))
stop_btn.pack(pady=5)
stop_btn.config(state='disabled')

disconnect_btn = tk.Button(btn_frame, text="Disconnect User", bg="#ff8c00", fg="white", width=15,
                           command=lambda: disconnect_user(user_listbox, chat_area))
disconnect_btn.pack(pady=5)

root.mainloop()