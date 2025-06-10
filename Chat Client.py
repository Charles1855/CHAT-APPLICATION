import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
import sqlite3
import os

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("TCP Chat Client")
        master.configure(bg="#f0f0f0")

        # Chat area
        self.chat_area = tk.Text(master, state='disabled', wrap=tk.WORD, bg="#ffffff", fg="#000000", font=("Segoe UI", 10))
        self.chat_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Message input
        self.entry = tk.Entry(master, width=40, font=("Segoe UI", 10))
        self.entry.pack(side=tk.LEFT, padx=(10, 0), pady=10)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(master, text="Send", command=self.send_message, bg="#4caf50", fg="white", font=("Segoe UI", 10, "bold"))
        self.send_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Text tag styles
        self.chat_area.tag_config("left", foreground="#800080", justify='left')   # Purple for others
        self.chat_area.tag_config("right", foreground="#008000", justify='right') # Green for self
        self.chat_area.tag_config("time_left", foreground="#999999", font=("Segoe UI", 8, "italic"), justify='left')
        self.chat_area.tag_config("time_right", foreground="#999999", font=("Segoe UI", 8, "italic"), justify='right')

        # Get user info
        self.username = simpledialog.askstring("Username", "Enter your name:")
        self.server_ip = simpledialog.askstring("Server IP", "Enter Server IP address:")
        self.port = 12345

        if not self.username or not self.server_ip:
            messagebox.showerror("Input Error", "Username and Server IP are required.")
            master.destroy()
            return

        # Setup database
        self.setup_database()
        self.load_chat_history()

        # Connect to server
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.port))
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Could not connect to server:\n{e}")
            master.destroy()
            return

        # Start receiving thread
        threading.Thread(target=self.receive_messages, daemon=True).start()

        # Handle window close
        master.protocol("WM_DELETE_WINDOW", self.close_connection)

    def setup_database(self):
        self.db_conn = sqlite3.connect("chat_history.db")
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                message TEXT,
                timestamp TEXT
            )
        """)
        self.db_conn.commit()

    def load_chat_history(self):
        self.chat_area.config(state='normal')
        self.db_cursor.execute("SELECT sender, message, timestamp FROM messages")
        for sender, message, timestamp in self.db_cursor.fetchall():
            align = "right" if sender == self.username else "left"
            self.chat_area.insert(tk.END, f"{sender}: {message}\n", align)
            self.chat_area.insert(tk.END, f"{' ' * (4 if align == 'left' else 20)}[{timestamp}]\n", f"time_{align}")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def save_message_to_db(self, sender, message, timestamp):
        self.db_cursor.execute("INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)",
                               (sender, message, timestamp))
        self.db_conn.commit()

    def send_message(self, event=None):
        msg = self.entry.get().strip()
        if msg:
            timestamp = datetime.now().strftime("%H:%M:%S")
            full_msg = f"{self.username}: {msg}"
            try:
                self.client_socket.sendall(full_msg.encode('utf-8'))
                self.display_message(f"You: {msg}", timestamp, align="right")
                self.save_message_to_db(self.username, msg, timestamp)
                self.entry.delete(0, tk.END)
            except:
                messagebox.showerror("Send Failed", "Message could not be sent.")
                self.master.destroy()

    def receive_messages(self):
        while True:
            try:
                msg = self.client_socket.recv(4096).decode('utf-8')
                if not msg:
                    break
                timestamp = datetime.now().strftime("%H:%M:%S")
                sender, message = msg.split(":", 1)
                self.display_message(msg, timestamp, align="left")
                self.save_message_to_db(sender.strip(), message.strip(), timestamp)
            except:
                break
        self.client_socket.close()
        self.master.quit()

    def display_message(self, msg, timestamp, align="left"):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, msg + "\n", align)
        self.chat_area.insert(tk.END, f"{' ' * (4 if align == 'left' else 20)}[{timestamp}]\n", f"time_{align}")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    def close_connection(self):
        try:
            self.client_socket.close()
            self.db_conn.close()
        except:
            pass
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
