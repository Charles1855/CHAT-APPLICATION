import socket
import threading
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
from datetime import datetime

HOST = 'localhost'
PORT = 12345
CHAT_HISTORY_FILE = 'client_chat_history.txt'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = ""

def current_time():
    return datetime.now().strftime("%H:%M")

def save_message(message):
    with open(CHAT_HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def load_chat_history(chat_area):
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                display_message(chat_area, line.strip(), from_history=True)

def display_message(chat_area, message, from_history=False):
    tag = 'right' if message.startswith("You [") or message.startswith(f"{username} [") else 'left'
    chat_area.config(state='normal')
    chat_area.insert(tk.END, message + "\n", tag)
    chat_area.config(state='disabled')
    chat_area.see(tk.END)
    if not from_history:
        save_message(message)

def update_user_list(user_listbox, user_list):
    user_listbox.delete(0, tk.END)
    for user in user_list:
        user_listbox.insert(tk.END, user)

def receive_messages(chat_area, user_listbox, status_label):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg.startswith("USERS:"):
                users = msg[6:].split(",")
                update_user_list(user_listbox, users)
            else:
                display_message(chat_area, msg)
        except:
            status_label.config(text="Disconnected")
            break

def send_message(entry, chat_area):
    msg = entry.get()
    if msg:
        timestamp = current_time()
        full_msg = f"{username} [{timestamp}]: {msg}"
        try:
            client_socket.send(full_msg.encode())
            display_message(chat_area, f"You [{timestamp}]: {msg}")
            entry.delete(0, tk.END)
        except:
            display_message(chat_area, "❌ Failed to send message")

def disconnect_client(root):
    try:
        client_socket.send("/quit".encode())
        client_socket.close()
    except:
        pass
    root.destroy()

def start_client(chat_area, user_listbox, status_label):
    global username
    try:
        client_socket.connect((HOST, PORT))
        username = simpledialog.askstring("Username", "Enter your username:")
        if not username:
            raise Exception("Username required")
        client_socket.send(username.encode())
        status_label.config(text=f"Connected as {username}")
        display_message(chat_area, f"Connected to {HOST}:{PORT}")
        load_chat_history(chat_area)
        threading.Thread(target=receive_messages, args=(chat_area, user_listbox, status_label), daemon=True).start()
    except Exception as e:
        display_message(chat_area, f"❌ Connection failed: {e}")
        status_label.config(text="Connection failed")

# GUI Setup
root = tk.Tk()
root.title("Chat Client")
root.geometry("720x480")
root.configure(bg="#f8f8f8")

# Main frames
main_frame = tk.Frame(root, bg="#f8f8f8")
main_frame.pack(expand=True, fill='both')

chat_frame = tk.Frame(main_frame)
chat_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=(10, 5), pady=10)

sidebar = tk.Frame(main_frame, bg="#f0f0f0", width=150)
sidebar.pack(side=tk.RIGHT, fill='y', padx=(5, 10), pady=10)

# Chat area
chat_area = tk.Text(chat_frame, wrap='word', state='disabled', font=("Segoe UI", 10))
chat_area.tag_configure('left', justify='left', foreground='blue')
chat_area.tag_configure('right', justify='right', foreground='green')
chat_area.pack(side=tk.LEFT, expand=True, fill='both')

scrollbar = ttk.Scrollbar(chat_frame, command=chat_area.yview)
scrollbar.pack(side=tk.RIGHT, fill='y')
chat_area.config(yscrollcommand=scrollbar.set)

# Entry and send
input_frame = tk.Frame(root, bg="#f8f8f8")
input_frame.pack(fill='x', padx=10, pady=(0, 10))

entry = ttk.Entry(input_frame)
entry.pack(side=tk.LEFT, padx=(0, 5), fill='x', expand=True)
entry.focus()

send_btn = ttk.Button(input_frame, text="Send", command=lambda: send_message(entry, chat_area))
send_btn.pack(side=tk.LEFT)

# Status & disconnect
bottom_frame = tk.Frame(root, bg="#f8f8f8")
bottom_frame.pack(fill='x', padx=10)

status_label = tk.Label(bottom_frame, text="Connecting...", anchor='w', bg="#f8f8f8")
status_label.pack(side=tk.LEFT)

disconnect_btn = ttk.Button(bottom_frame, text="Disconnect", command=lambda: disconnect_client(root))
disconnect_btn.pack(side=tk.RIGHT)

# Sidebar user list
tk.Label(sidebar, text="Online Users", bg="#f0f0f0", font=("Segoe UI", 10, "bold")).pack(pady=(0, 5))
user_listbox = tk.Listbox(sidebar)
user_listbox.pack(fill='y', expand=True)

start_client(chat_area, user_listbox, status_label)

root.protocol("WM_DELETE_WINDOW", lambda: disconnect_client(root))
root.mainloop()