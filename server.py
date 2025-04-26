import socket
import threading
import json
import os
from datetime import datetime

class ChatServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        
        self.clients = {}
        self.files = {}
        self.file_dir = "server_files"
        os.makedirs(self.file_dir, exist_ok=True)
        
        print(f"Server started on {host}:{port}")
        self.running = True
        self.accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
        self.accept_thread.start()
    
    def accept_connections(self):
        while self.running:
            try:
                client, address = self.server_socket.accept()
                print(f"Connection from {address}")
                
                threading.Thread(
                    target=self.handle_client,
                    args=(client,),
                    daemon=True
                ).start()
            except:
                break
    
    def handle_client(self, client):
        try:
            # Get nickname first (with timeout)
            client.settimeout(5.0)
            nickname_data = client.recv(1024)
            if not nickname_data:
                raise ConnectionError("No nickname received")
            
            nickname = json.loads(nickname_data.decode('utf-8')).get('nickname', 'Unknown')
            self.clients[client] = {"nickname": nickname, "address": client.getpeername()}
            
            # Send welcome message
            client.sendall(json.dumps({
                "type": "CONNECTION_SUCCESS",
                "message": f"Welcome, {nickname}!"
            }).encode('utf-8'))

            # Reset timeout
            client.settimeout(None)
            
            # Broadcast join message
            self.broadcast({
                "type": "SYSTEM_MESSAGE",
                "message": f"{nickname} joined the chat",
                "time": datetime.now().strftime("%H:%M")
            })
            
            # Send user list
            self.update_user_list()
            
            # Main message loop
            while True:
                try:
                    data = client.recv(4096)
                    if not data:
                        break
                    
                    message = json.loads(data.decode('utf-8'))
                    self.handle_message(client, nickname, message)
                
                except json.JSONDecodeError:
                    continue
                except ConnectionResetError:
                    break
        
        except Exception as e:
            print(f"Client error: {str(e)}")
        finally:
            self.remove_client(client)
    
    def handle_message(self, client, nickname, message):
        if message['type'] == 'TEXT_MESSAGE':
            self.broadcast({
                "type": "TEXT_MESSAGE",
                "sender": nickname,
                "message": message['message'],
                "time": datetime.now().strftime("%H:%M")
            })
        elif message['type'] == 'WHISPER':
            target = message['target']
            for cli, data in self.clients.items():
                if data['nickname'] == target:
                    cli.sendall(json.dumps({
                        "type": "WHISPER",
                        "sender": nickname,
                        "message": message['message'],
                        "time": datetime.now().strftime("%H:%M")
                    }).encode('utf-8'))
        elif message['type'] == 'FILE_METADATA':
            self.handle_file_upload(client, nickname, message)
        elif message['type'] == 'FILE_REQUEST':
            self.handle_file_download(client, message['filename'])
        
    def handle_file_upload(self, client, nickname, metadata):
        try:
            filename = metadata['filename']
            filesize = int(metadata['size'])
            target = metadata.get('target')

            # Create safe filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
            filepath = os.path.join(self.file_dir, safe_filename)

            # Send acknowledgment
            client.sendall(json.dumps({
                "type": "FILE_ACK",
                "status": "ready",
                "filename": safe_filename
            }).encode('utf-8'))

            # Receive file data
            received = 0
            with open(filepath, 'wb') as f:
                while received < filesize:
                    chunk = client.recv(min(8192, filesize - received))
                    if not chunk:
                        raise ConnectionError("Transfer interrupted")
                    f.write(chunk)
                    received += len(chunk)

            # Store file info
            self.files[safe_filename] = {
                'path': filepath,
                'size': filesize,
                'sender': nickname,
                'time': datetime.now().strftime("%H:%M")
            }

            # Notify clients
            file_message = {
                "type": "FILE_AVAILABLE",
                "filename": safe_filename,
                "size": filesize,
                "sender": nickname,
                "private": bool(target),
                "time": datetime.now().strftime("%H:%M")
            }

            if target:
                # Send to specific target
                for cli, data in self.clients.items():
                    if data['nickname'] == target or data['nickname'] == nickname:
                        cli.sendall(json.dumps(file_message).encode('utf-8'))
            else:
                # Broadcast to all
                self.broadcast(file_message)

        except Exception as e:
            print(f"File transfer error: {str(e)}")
            try:
                client.sendall(json.dumps({
                    "type": "FILE_ACK",
                    "status": "error",
                    "message": str(e)
                }).encode('utf-8'))
            except:
                pass

    
    def handle_file_download(self, client, filename):
        if filename not in self.files:
            return
        
        filepath = self.files[filename]['path']
        
        try:
            # Send file metadata
            client.sendall(json.dumps({
                "type": "FILE_START",
                "filename": filename,
                "size": self.files[filename]['size']
            }).encode('utf-8'))
            
            # Send file data
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(8192)
                    if not data:
                        break
                    client.sendall(data)
        
        except Exception as e:
            print(f"File download error: {str(e)}")
    
    def broadcast(self, message):
        message_json = json.dumps(message)
        for client in list(self.clients.keys()):
            try:
                client.sendall(message_json.encode('utf-8'))
            except:
                self.remove_client(client)
    
    def update_user_list(self):
        user_list = {
            "type": "USER_LIST",
            "users": [data['nickname'] for data in self.clients.values()]
        }
        self.broadcast(user_list)
    
    def remove_client(self, client):
        if client in self.clients:
            nickname = self.clients[client]['nickname']
            del self.clients[client]
            client.close()
            
            self.broadcast({
                "type": "SYSTEM_MESSAGE",
                "message": f"{nickname} left the chat",
                "time": datetime.now().strftime("%H:%M")
            })
            self.update_user_list()
    
    def shutdown(self):
        self.running = False
        self.server_socket.close()

if __name__ == "__main__":
    server = ChatServer()
    try:
        server.accept_thread.join()
    except KeyboardInterrupt:
        server.shutdown()