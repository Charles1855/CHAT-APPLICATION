import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class ChatServerGUI:
    def init(self, master):
        self.master = master
        master.title("TCP Chat Server")

        self.text_area = scrolledtext.ScrolledText(master, state='disabled', wrap=tk.WORD, width=60, height=25)
        self.text_area.pack(padx=10, pady=(10, 0))

        # Frame for buttons
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(button_frame, text="Stop Server", command=self.stop_server, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=10)

        self.server_socket = None
        self.clients = []
        self.is_running = False

        self.HOST = '0.0.0.0'
        self.PORT = 12345
        self.lock = threading.Lock()

    def log(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled')

    def broadcast(self, message, sender_socket):
        with self.lock:
            for client in list(self.clients):
                if client != sender_socket:
                    try:
                        client.sendall(message)
                    except:
                        client.close()
                        self.clients.remove(client)

    def handle_client(self, client_socket, address):
        self.log(f"[+] Connected: {address}")
        with self.lock:
            self.clients.append(client_socket)

        try:
            while self.is_running:
                msg = client_socket.recv(1024)
                if not msg:
                    break
                self.log(f"[MSG] {address}: {msg.decode('utf-8')}")
                self.broadcast(msg, client_socket)
        except:
            pass
        finally:
            with self.lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            client_socket.close()
            self.log(f"[-] Disconnected: {address}")

    def accept_clients(self):
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True).start()
            except:
                break  # Likely the server socket was closed

    def start_server(self):
        if self.is_running:
            return
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.HOST, self.PORT))
            self.server_socket.listen()
            self.is_running = True
            self.log(f"[SERVER STARTED] Listening on {self.HOST}:{self.PORT}")

            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')

            threading.Thread(target=self.accept_clients, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server:\n{e}")

    def stop_server(self):
        if not self.is_running:
            return
        self.is_running = False
        self.log("[SERVER STOPPING]")

        try:
            if self.server_socket:
                self.server_socket.close()
        except:
            pass

        with self.lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()

        self.log("[SERVER STOPPED]")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def on_close(self):
        self.stop_server()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()