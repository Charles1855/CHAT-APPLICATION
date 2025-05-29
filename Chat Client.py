# chat_client_gui.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = 'localhost'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def receive_messages(chat_area):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            chat_area.insert(tk.END, msg + '\n')
        except:
            break

def send_message(entry, chat_area):
    msg = entry.get()
    if msg:
        client_socket.send(msg.encode())
        chat_area.insert(tk.END, f"You: {msg}\n")
        entry.delete(0, tk.END)

def start_client(chat_area):
    try:
        client_socket.connect((HOST, PORT))
        chat_area.insert(tk.END, f"Connected to server {HOST}:{PORT}\n")
        threading.Thread(target=receive_messages, args=(chat_area,), daemon=True).start()
    except:
        chat_area.insert(tk.END, "Connection failed\n")

# GUI Setup
root = tk.Tk()
root.title("Chat Client")

chat_area = scrolledtext.ScrolledText(root, width=60, height=20, state='normal')
chat_area.pack(padx=10, pady=10)

entry = tk.Entry(root, width=40)
entry.pack(side=tk.LEFT, padx=10, pady=5)

send_btn = tk.Button(root, text="Send", command=lambda: send_message(entry, chat_area))
send_btn.pack(side=tk.LEFT)

start_client(chat_area)

root.mainloop()