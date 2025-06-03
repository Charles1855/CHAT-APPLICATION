import socket
import threading
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk
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

def receive_messages(chat_area, status_label):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
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
            display_message(chat_area, "Error: Could not send message")

def start_client(chat_area, status_label):
    try:
        client_socket.connect((HOST, PORT))
        status_label.config(text=f"Connected as {username}")
        display_message(chat_area, f"Connected to server at {HOST}:{PORT}")
        load_chat_history(chat_area)
        threading.Thread(target=receive_messages, args=(chat_area, status_label), daemon=True).start()
    except:
        display_message(chat_area, "Connection failed")
        status_label.config(text="Connection failed")

# GUI Setup
root.title(f"Chat Client - {username}")
root.geometry("600x450")
root.configure(bg="#f0f0f0")

# Frame for chat display
chat_frame = ttk.Frame(root, padding=10)
chat_frame.pack(expand=True, fill='both')

chat_area = tk.Text(chat_frame, wrap='word', state='disabled', font=("Segoe UI", 10))
chat_area.tag_configure('left', justify='left')
chat_area.tag_configure('right', justify='right')
chat_area.tag_configure('center', justify='center')
chat_area.tag_configure('green', foreground='green')
chat_area.tag_configure('blue', foreground='blue')
chat_area.tag_configure('gray', foreground='gray')
chat_area.pack(side=tk.LEFT, expand=True, fill='both')

scrollbar = ttk.Scrollbar(chat_frame, command=chat_area.yview)
scrollbar.pack(side=tk.RIGHT, fill='y')
chat_area.config(yscrollcommand=scrollbar.set)

# Frame for entry and send button
input_frame = ttk.Frame(root, padding=10)
input_frame.pack(fill='x')

entry = ttk.Entry(input_frame, width=50)
entry.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill='x')
entry.focus()

send_btn = ttk.Button(input_frame, text="Send", command=lambda: send_message(entry, chat_area))
send_btn.pack(side=tk.RIGHT)

# Status bar
status_label = ttk.Label(root, text="Connecting...", anchor='w', padding=5, relief="sunken")
status_label.pack(fill='x', side=tk.BOTTOM)

start_client(chat_area, status_label)

root.mainloop()