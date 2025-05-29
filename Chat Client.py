import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = 'localhost'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = ""
typing = False
typing_timer = None

def receive_messages(chat_area, typing_label):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg.startswith("TYPING_START:"):
                user = msg.split(":", 1)[1]
                if user != username:
                    typing_label.config(text=f"{user} is typing...")
            elif msg.startswith("TYPING_STOP:"):
                user = msg.split(":", 1)[1]
                if user != username:
                    typing_label.config(text="")
            else:
                chat_area.insert(tk.END, msg + '\n')
        except:
            break

def send_message(entry, chat_area, typing_label):
    global typing
    msg = entry.get().strip()
    if msg:
        try:
            client_socket.send(msg.encode())
            chat_area.insert(tk.END, f"You: {msg}\n")
            entry.delete(0, tk.END)
            stop_typing()
            typing_label.config(text="")
        except:
            chat_area.insert(tk.END, "Failed to send message\n")

def on_typing(event):
    global typing, typing_timer
    if not typing:
        typing = True
        client_socket.send(f"TYPING_START:{username}".encode())

    if typing_timer:
        root.after_cancel(typing_timer)
    typing_timer = root.after(20000, stop_typing)

def stop_typing():
    global typing
    if typing:
        typing = False
        try:
            client_socket.send(f"TYPING_STOP:{username}".encode())
        except:
            pass

def connect(chat_area, typing_label, username_entry, connect_btn):
    global username
    username = username_entry.get().strip()
    if not username:
        chat_area.insert(tk.END, "Enter a username.\n")
        return

    try:
        client_socket.connect((HOST, PORT))
        client_socket.send(username.encode())
        chat_area.insert(tk.END, f"Connected as {username}\n")
        threading.Thread(target=receive_messages, args=(chat_area, typing_label), daemon=True).start()
        connect_btn.config(state=tk.DISABLED)
    except:
        chat_area.insert(tk.END, "Failed to connect to server.\n")

# GUI setup
root = tk.Tk()
root.title("Chat Client")

chat_area = scrolledtext.ScrolledText(root, width=60, height=20)
chat_area.pack(padx=10, pady=5)

typing_label = tk.Label(root, text="", fg="gray")
typing_label.pack()

username_frame = tk.Frame(root)
username_frame.pack(pady=2)
tk.Label(username_frame, text="Username:").pack(side=tk.LEFT)
username_entry = tk.Entry(username_frame, width=20)
username_entry.pack(side=tk.LEFT)

entry_frame = tk.Frame(root)
entry_frame.pack(pady=5)

entry = tk.Entry(entry_frame, width=40)
entry.pack(side=tk.LEFT, padx=5)
entry.bind("<KeyRelease>", on_typing)

send_button = tk.Button(entry_frame, text="Send", command=lambda: send_message(entry, chat_area, typing_label))
send_button.pack(side=tk.LEFT)

connect_button = tk.Button(root, text="Connect", command=lambda: connect(chat_area, typing_label, username_entry, connect_button))
connect_button.pack()

root.mainloop()