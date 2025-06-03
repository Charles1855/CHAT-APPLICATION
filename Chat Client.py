import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
from datetime import datetime

HOST = 'localhost'
PORT = 12345
CHAT_HISTORY_FILE = 'client_chat_history.txt'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = ""
connected = False

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
    tag = 'right' if message.startswith("You [") else 'left'
    chat_area.config(state='normal')
    chat_area.insert(tk.END, message + "\n", tag)
    chat_area.config(state='disabled')
    chat_area.see(tk.END)
    if not from_history:
        save_message(message)

def receive_messages(chat_area):
    global connected
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg == "/banned":
                messagebox.showwarning("Banned", "You are banned from the server.")
                root.destroy()
                return
            display_message(chat_area, msg)
        except:
            break

def send_message(entry, chat_area):
    msg = entry.get()
    if msg and connected:
        timestamp = current_time()
        full_msg = f"{username} [{timestamp}]: {msg}"
        try:
            client_socket.send(full_msg.encode())
            display_message(chat_area, f"You [{timestamp}]: {msg}")
            entry.delete(0, tk.END)
        except:
            display_message(chat_area, "❌ Failed to send message")

def start_client(name_entry, chat_area, entry, join_btn):
    global username, connected
    username = name_entry.get().strip()
    if not username:
        messagebox.showerror("Error", "Please enter a username.")
        return
    try:
        client_socket.connect((HOST, PORT))
        client_socket.send(username.encode())
        connected = True
        display_message(chat_area, f"✅ Connected to server as {username}")
        name_entry.config(state='disabled')
        entry.config(state='normal')
        join_btn.config(state='disabled')
        load_chat_history(chat_area)
        threading.Thread(target=receive_messages, args=(chat_area,), daemon=True).start()
    except Exception as e:
        display_message(chat_area, f"❌ Connection failed: {e}")

# GUI
root = tk.Tk()
root.title("Chat Client")
root.geometry("700x500")
root.config(bg="#f0f8ff")

top_frame = tk.Frame(root, bg="#f0f8ff")
top_frame.pack(pady=10)

tk.Label(top_frame, text="Username:", bg="#f0f8ff").pack(side=tk.LEFT)
name_entry = tk.Entry(top_frame, width=20)
name_entry.pack(side=tk.LEFT, padx=5)

join_btn = tk.Button(top_frame, text="Join", bg="#00bfff", fg="white",
                     command=lambda: start_client(name_entry, chat_area, entry, join_btn))
join_btn.pack(side=tk.LEFT)

chat_area = scrolledtext.ScrolledText(root, width=80, height=20, state='disabled', font=("Segoe UI", 10))
chat_area.tag_configure('left', justify='left', foreground='blue')
chat_area.tag_configure('right', justify='right', foreground='green')
chat_area.pack(padx=10, pady=5)

bottom_frame = tk.Frame(root, bg="#f0f8ff")
bottom_frame.pack(pady=10)

entry = tk.Entry(bottom_frame, width=50)
entry.pack(side=tk.LEFT, padx=5)
entry.config(state='disabled')

send_btn = tk.Button(bottom_frame, text="Send", bg="#32cd32", fg="white",
                     command=lambda: send_message(entry, chat_area))
send_btn.pack(side=tk.LEFT)

root.mainloop()