import socket
import threading
import tkinter as tk
from tkinter import simpledialog
import os
from datetime import datetime

HOST = 'localhost'
PORT = 12345
CHAT_HISTORY_FILE = 'client_chat_history.txt'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Prompt for username
root = tk.Tk()
root.withdraw()
username = simpledialog.askstring("Username", "Enter your display name:")
root.deiconify()

def current_time():
    return datetime.now().strftime("%H:%M")

def save_message_to_file(message):
    with open(CHAT_HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(message + "\n")

def load_chat_history(chat_area):
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                display_message(chat_area, line.strip(), from_history=True)

def display_message(chat_area, message, from_history=False):
    if message.startswith("You [") or message.startswith(f"{username} ["):
        tag = 'left'
        color = 'green'
    elif message.startswith("Connected to") or "disconnected" in message:
        tag = 'center'
        color = 'gray'
    else:
        tag = 'right'
        color = 'blue'

    chat_area.config(state='normal')
    chat_area.insert(tk.END, message + "\n", (tag, color))
    chat_area.config(state='disabled')
    chat_area.see(tk.END)

    if not from_history:
        save_message_to_file(message)

def receive_messages(chat_area):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                display_message(chat_area, msg)
        except:
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
            display_message(chat_area, "Error: Could not send message")

def start_client(chat_area):
    try:
        client_socket.connect((HOST, PORT))
        display_message(chat_area, f"Connected to server at {HOST}:{PORT}")
        load_chat_history(chat_area)
        threading.Thread(target=receive_messages, args=(chat_area,), daemon=True).start()
    except:
        display_message(chat_area, "Connection failed")

# GUI Setup
root.title(f"Chat Client - {username}")

chat_area = tk.Text(root, width=60, height=20, wrap='word', state='disabled')
chat_area.tag_configure('left', justify='left')
chat_area.tag_configure('right', justify='right')
chat_area.tag_configure('center', justify='center')

chat_area.tag_configure('green', foreground='green')
chat_area.tag_configure('blue', foreground='blue')
chat_area.tag_configure('gray', foreground='gray')

chat_area.pack(padx=10, pady=10)

entry = tk.Entry(root, width=40)
entry.pack(side=tk.LEFT, padx=10, pady=5)

send_btn = tk.Button(root, text="Send", command=lambda: send_message(entry, chat_area))
send_btn.pack(side=tk.LEFT)

start_client(chat_area)

root.mainloop()