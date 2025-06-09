 Python Chat Application 

This is a Python-based client-server chat application that allows multiple users to connect and exchange messages over a local network using sockets and Tkinter. The application supports real-time messaging, typing indicators, chat history, and server controls (start, stop, disconnect user).

How IP Address and Port Work

- **IP Address**: Uniquely identifies a device on a network. The server listens on an IP (e.g., `192.168.1.100`) to accept incoming connections.
- **Port**: A communication endpoint on a device. Both client and server must use the same port (e.g., `12345`) to establish a connection.

Features

- GUI for both client and server
- Real-time messaging
- Chat history saving (client side)
- Typing indicator
- Server can:
  - Start/Stop listening
  - Disconnect specific users
- Cross-laptop chat using Ethernet or Wi-Fi LAN
 
Setup Instructions
Requirements

- Python 3.x
- Standard libraries (`socket`, `tkinter`, etc.)

On the Server Laptop

1. Find the server's IP address (e.g., run `ipconfig` on Windows or `ifconfig` on Linux/Mac).
2. Open `server.py` and run it:
   ```bash
   python server.py
   ```

On the Client Laptop(s)

1. Make sure the server and clients are on the **same network** (via Wi-Fi or Ethernet).
2. Open and run `client.py`:
   ```bash
   python client.py
   ```
3. Enter the server's IP address and your username to join the chat.

---

Key Functions Overview

`server.py`

- `start_server()`: Starts listening on `0.0.0.0:PORT` and accepts new clients.
- `broadcast()`: Sends messages to all clients except the sender.
- `handle_client()`: Receives and handles incoming messages from a client.
- `disconnect_user()`: Allows server admin to remove a specific user.
- `stop_server()`: Stops server and closes all connections.

`client.py`

- `start_client()`: Connects to server using IP and port provided by user.
- `receive_messages()`: Continuously listens for server messages.
- `send_message()`: Sends user's input to the server and saves it.
- `load_chat_history()`: Loads messages from previous sessions.
- `display_message()`: Shows messages with formatting in the GUI.


Example Scenario

1. **Server IP**: `192.168.1.5`
2. **Port**: `12345`
3. **Client 1 IP**: `192.168.1.6`, connects with username `Alice`
4. **Client 2 IP**: `192.168.1.7`, connects with username `Bob`
5. Both clients send and receive messages from the server which relays them to everyone.


Optional Enhancements

- Add encryption (TLS sockets)
- Add file sharing
- Improve UI with emojis or themes

This project is provided for educational purposes. Free to modify and redistribute.
