import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
import json

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("TCP Chat Client")
        master.configure(bg="#f0f0f0")

        # Chat display area
        self.chat_area = tk.Text(master, state='disabled', wrap=tk.WORD, bg="#ffffff", fg="#000000", font=("Segoe UI", 10))
        self.chat_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Entry and Send Button
        self.entry = tk.Entry(master, width=40, font=("Segoe UI", 10))
        self.entry.pack(side=tk.LEFT, padx=(10, 0), pady=10)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(master, text="Send", command=self.send_message, bg="#4caf50", fg="white", font=("Segoe UI", 10, "bold"))
        self.send_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Tags
        self.chat_area.tag_config("left", foreground="#800080", justify='left')   # Purple
        self.chat_area.tag_config("right", foreground="#008000", justify='right') # Green
        self.chat_area.tag_config("time_left", foreground="#999999", font=("Segoe UI", 8, "italic"), justify='left')
        self.chat_area.tag_config("time_right", foreground="#999999", font=("Segoe UI", 8, "italic"), justify='right')

        # User and server info
        self.username = simpledialog.askstring("Username", "Enter your name:")
        self.server_ip = simpledialog.askstring("Server IP", "Enter Server IP address:")
        self.port = 12345

        if not self.username or not self.server_ip:
            messagebox.showerror("Input Error", "Username and Server IP are required.")
            master.destroy()
            return

        # Load chat history from file
        self.chat_history_file = "chat_history.txt"
        self.load_chat_history()

        # Connect to server
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.port))
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Could not connect to server:\n{e}")
            master.destroy()
            return

        threading.Thread(target=self.receive_messages, daemon=True).start()
        master.protocol("WM_DELETE_WINDOW", self.close_connection)

    def load_chat_history(self):
        try:
            with open(self.chat_history_file, "r", encoding="utf-8") as f:
                self.chat_area.config(state='normal')
                for line in f:
                    self.chat_area.insert(tk.END, line)
                self.chat_area.config(state='disabled')
                self.chat_area.yview(tk.END)
        except FileNotFoundError:
            # No history yet, ignore
            pass

    def save_message_to_file(self, msg):
        try:
            with open(self.chat_history_file, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except Exception as e:
            print(f"Error writing to chat history file: {e}")

    def send_message(self, event=None):
        msg = self.entry.get().strip()
        if msg:
            timestamp = datetime.now().strftime("%H:%M:%S")
            data = json.dumps({"sender": self.username, "message": msg}) + "\n"  # Append newline delimiter
            try:
                self.client_socket.sendall(data.encode('utf-8'))
                display_msg = f"You: {msg}\n{' ' * 20}[{timestamp}]\n"
                self.display_message(display_msg, align="right")
                self.save_message_to_file(display_msg)
                self.entry.delete(0, tk.END)
            except Exception as e:
                print(f"Send error: {e}")
                messagebox.showerror("Send Failed", f"Message could not be sent:\n{e}")
                self.close_connection()

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    print("Server closed connection.")
                    break
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if not line.strip():
                        continue
                    try:
                        msg_data = json.loads(line)
                        sender = msg_data.get("sender", "Unknown")
                        message = msg_data.get("message", "")
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        display_msg = f"{sender}: {message}\n{' ' * 4}[{timestamp}]\n"
                        self.display_message(display_msg, align="left")
                        self.save_message_to_file(display_msg)
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e} with data: {line}")
            except Exception as e:
                print(f"Receive error: {e}")
                break
        self.client_socket.close()
        self.master.quit()

    def display_message(self, msg, align="left"):
        self.chat_area.config(state='normal')
        tag = "right" if align == "right" else "left"
        self.chat_area.insert(tk.END, msg, tag)
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    def close_connection(self):
        try:
            self.client_socket.close()
        except:
            pass
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
