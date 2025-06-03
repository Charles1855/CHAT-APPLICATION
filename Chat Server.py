import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

HOST = 'localhost'
PORT = 12345

clients = {}  # {socket: username}
banned_users = {}  # {username: unban_time (float)}

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
        if username in banned_users:
            client_socket.send("/banned".encode())
            client_socket.close()
            return
        clients[client_socket] = username
        update_user_list(user_listbox)
        broadcast(f"{username} joined the chat.", client_socket)
        chat_area.insert(tk.END, f"{username} connected.\n")

        while True:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
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

def start_server(chat_area, user_listbox):
    def run():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()
        chat_area.insert(tk.END, f"Server started on {HOST}:{PORT}\n")
        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr, chat_area, user_listbox), daemon=True).start()

    threading.Thread(target=run, daemon=True).start()

def ban_user(user_listbox, chat_area):
    try:
        selected = user_listbox.get(user_listbox.curselection())
        duration = simpledialog.askinteger("Ban Duration", f"How many seconds should {selected} be banned?")
        if duration is None:
            return
        for sock, name in list(clients.items()):
            if name == selected:
                banned_users[name] = time.time() + duration
                sock.send("/banned".encode())
                sock.close()
                del clients[sock]
                update_user_list(user_listbox)
                broadcast(f"{name} has been banned.")
                chat_area.insert(tk.END, f"{name} was banned for {duration} seconds.\n")
                break
    except:
        messagebox.showerror("Error", "No user selected.")

def disconnect_user(user_listbox, chat_area):
    try:
        selected = user_listbox.get(user_listbox.curselection())
        for sock, name in list(clients.items()):
            if name == selected:
                sock.send("You have been disconnected.".encode())
                sock.close()
                del clients[sock]
                update_user_list(user_listbox)
                broadcast(f"{name} has been disconnected.")
                chat_area.insert(tk.END, f"{name} was disconnected.\n")
                break
    except:
        messagebox.showerror("Error", "No user selected.")

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
                      command=lambda: start_server(chat_area, user_listbox))
start_btn.pack(pady=5)

ban_btn = tk.Button(btn_frame, text="Ban User", bg="#ff6347", fg="white", width=15,
                    command=lambda: ban_user(user_listbox, chat_area))
ban_btn.pack(pady=5)

kick_btn = tk.Button(btn_frame, text="Disconnect User", bg="#ffa500", fg="white", width=15,
                     command=lambda: disconnect_user(user_listbox, chat_area))
kick_btn.pack(pady=5)

root.mainloop()