import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ChatServerGUI:
    def _init_(self, master):
        self.master = master
        master.title("TCP Chat Server")
        master.geometry("600x400")

        self.start_button = tk.Button(master, text="Start Server", command=self.start_server, bg="#4caf50", fg="white")
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop Server", command=self.stop_server, bg="#f44336", fg="white", state='disabled')
        self.stop_button.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(master, state='disabled', bg="#ffffff", fg="#000000", wrap=tk.WORD)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.clients = []
        self.server_socket = None
        self.running = False

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.config(state='disabled')
        self.log_area.yview(tk.END)

    def start_server(self):
        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        threading.Thread(target=self.run_server, daemon=True).start()
        self.log("[SERVER] Starting...")

    def run_server(self, host='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((host, port))
            self.server_socket.listen()
            self.log(f"[SERVER] Listening on {host}:{port}")
        except Exception as e:
            self.log(f"[ERROR] Could not start server: {e}")
            return

        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.clients.append(client_socket)
                self.log(f"[CONNECTED] {address}")
                threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True).start()
            except:
                break

    def handle_client(self, client_socket, address):
        while self.running:
            try:
                msg = client_socket.recv(4096)
                if not msg:
                    break
                decoded = msg.decode('utf-8')
                self.log(f"[{address}] {decoded}")
                self.broadcast(decoded, client_socket)
            except:
                break
        self.log(f"[DISCONNECTED] {address}")
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()

    def broadcast(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.sendall(message.encode('utf-8'))
                except:
                    if client in self.clients:
                        self.clients.remove(client)

    def stop_server(self):
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        try:
            for client in self.clients:
                client.close()
            self.clients.clear()
            if self.server_socket:
                self.server_socket.close()
            self.log("[SERVER] Server stopped.")
        except Exception as e:
            self.log(f"[ERROR] Failed to stop server: {e}")

    def on_close(self):
        if self.running:
            self.stop_server()
        self.master.destroy()

if _name_ == "_main_":
    root = tk.Tk()
    server_gui = ChatServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", server_gui.on_close)
    root.mainloop()