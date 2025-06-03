import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog
import os

HOST = 'localhost'
PORT = 12345
CHAT_HISTORY_FILE = 'client_chat_history.txt'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Prompt for username
root = tk.Tk()
root.withdraw()  # Hide while prompting
username = simpledialog.askstring("Username", "Enter your display name:")
root.deiconify()

def save_message_to_file(message):
    """Append message to local chat history file."""
    with open(CHAT_HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(message + "\n")

def load_chat_history(chat_area):
    """Load chat history from file into the chat area."""
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                chat_area.insert(tk.END, line)

def receive_messages(chat_area):
    """Receive and display messages from the server."""
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                chat_area.insert(tk.END, msg + '\n')
                save_message_to_file(msg)
        except:
            break

def send_message(entry, chat_area):
    """Send a message and display it locally."""
    msg = entry.get()
    if msg:
        full_msg = f"{username}: {msg}"
        try:
            client_socket.send(full_msg.encode())
            chat_area.insert(tk.END, f"You: {msg}\n")
            save_message_to_file(f"You: {msg}")
            entry.delete(0, tk.END)
        except:
            chat_area.insert(tk.END, "Error: Could not send message\n")

def start_client(chat_area):
    try:
        client_socket.connect((HOST, PORT))
        chat_area.insert(tk.END, f"Connected to server at {HOST}:{PORT}\n")
        load_chat_history(chat_area)
        threading.Thread(target=receive_messages, args=(chat_area,), daemon=True).start()
    except:
        chat_area.insert(tk.END, "Connection failed\n")

# GUI Setup
root.title("Chat Client")

chat_area = scrolledtext.ScrolledText(root, width=60, height=20, state='normal')
chat_area.pack(padx=10, pady=10)

entry = tk.Entry(root, width=40)
entry.pack(side=tk.LEFT, padx=10, pady=5)

send_btn = tk.Button(root, text="Send", command=lambda: send_message(entry, chat_area))
send_btn.pack(side=tk.LEFT)

start_client(chat_area)

root.mainloop()