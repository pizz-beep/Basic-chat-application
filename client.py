import os
import json
import socket
import threading
import emoji
from tkinter import *
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
from styles import Styles
from emoji_picker import EmojiPicker
import sounddevice as sd
from scipy.io.wavfile import write

class ModernChatClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_dir = "client_files"
        os.makedirs(self.file_dir, exist_ok=True)
        self.whisper_target = None
        
        # Create root window
        self.root = Tk()
        self.root.title("Modern Chat")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize styles
        self.styles = Styles(self.root)
        self.root.configure(bg=self.styles.bg_dark)
        
        # Configure grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.setup_gui()
        self.root.mainloop()
    

    def setup_gui(self):
        # Connection bar
        self.connection_frame = Frame(self.root, bg=self.styles.bg_medium, padx=15, pady=10)
        self.connection_frame.grid(row=0, column=0, sticky="ew")
        
        # Server connection controls
        Label(self.connection_frame, text="Server:", bg=self.styles.bg_medium, 
            fg=self.styles.text_primary, font=self.styles.font_normal).pack(side=LEFT)
        
        self.ip_entry = Entry(self.connection_frame, width=15, bg=self.styles.bg_input, 
                            fg=self.styles.text_primary, insertbackground="white",
                            font=self.styles.font_normal, relief=FLAT)
        self.ip_entry.pack(side=LEFT, padx=5)
        self.ip_entry.insert(0, "127.0.0.1")
        
        Label(self.connection_frame, text="Port:", bg=self.styles.bg_medium, 
            fg=self.styles.text_primary, font=self.styles.font_normal).pack(side=LEFT)
        
        self.port_entry = Entry(self.connection_frame, width=5, bg=self.styles.bg_input, 
                            fg=self.styles.text_primary, insertbackground="white",
                            font=self.styles.font_normal, relief=FLAT)
        self.port_entry.pack(side=LEFT, padx=5)
        self.port_entry.insert(0, "5555")
        
        Label(self.connection_frame, text="Name:", bg=self.styles.bg_medium, 
            fg=self.styles.text_primary, font=self.styles.font_normal).pack(side=LEFT)
        
        self.nick_entry = Entry(self.connection_frame, width=15, bg=self.styles.bg_input, 
                            fg=self.styles.text_primary, insertbackground="white",
                            font=self.styles.font_normal, relief=FLAT)
        self.nick_entry.pack(side=LEFT, padx=5)
        self.nick_entry.insert(0, "User1")
        
        self.connect_btn = Button(self.connection_frame, text="Connect", 
                                command=self.connect_to_server, **self.styles.button_style)
        self.connect_btn.pack(side=LEFT, padx=5)
        
        self.disconnect_btn = Button(self.connection_frame, text="Disconnect", 
                                command=self.disconnect, state=DISABLED,
                                **self.styles.secondary_button_style)
        self.disconnect_btn.pack(side=LEFT)
        
        # Main chat area
        self.main_frame = Frame(self.root, bg=self.styles.bg_dark)
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=WORD,
            bg=self.styles.bg_dark,
            fg=self.styles.text_primary,
            insertbackground="white",
            font=self.styles.font_normal,
            padx=15,
            pady=15,
            state='disabled'    
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew")
        self.chat_display.config(state='disabled')
        
        # Configure tags
        self.chat_display.tag_config("time", foreground=self.styles.text_secondary, font=self.styles.font_small)
        self.chat_display.tag_config("username", foreground=self.styles.accent, font=self.styles.font_small)
        self.chat_display.tag_config("message", font=self.styles.font_normal)
        self.chat_display.tag_config("whisper", foreground=self.styles.accent)
        self.chat_display.tag_config("system", foreground=self.styles.text_secondary, font=self.styles.font_small)
        self.chat_display.tag_config("bubble_left", background=self.styles.bg_light, 
                                relief=SOLID, borderwidth=1, lmargin1=10, 
                                lmargin2=10, rmargin=100, spacing3=5)
        self.chat_display.tag_config("bubble_right", background=self.styles.accent, 
                                    relief=SOLID, borderwidth=1, lmargin1=100, 
                                    lmargin2=10, rmargin=10, spacing3=5)
        
        # Input area
        self.input_frame = Frame(self.main_frame, bg=self.styles.bg_medium, padx=10, pady=10)
        self.input_frame.grid(row=1, column=0, sticky="ew")
        
        # Emoji button
        self.emoji_btn = Button(
            self.input_frame,
            text="😊",
            command=self.show_emoji_picker,
            **self.styles.secondary_button_style
        )
        self.emoji_btn.pack(side=LEFT)
        
        # Message entry
        self.message_entry = Entry(
            self.input_frame,
            bg=self.styles.bg_input,
            fg=self.styles.text_primary,
            insertbackground="white",
            font=self.styles.font_normal,
            relief=FLAT
        )
        self.message_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.message_entry.bind("<Return>", self.send_message)
        
        # File button
        self.file_btn = Button(
            self.input_frame,
            text="📎",
            command=self.send_file_dialog,
            state=DISABLED,
            **self.styles.secondary_button_style
        )
        self.file_btn.pack(side=LEFT, padx=5)
        
        # Send button
        self.send_btn = Button(
            self.input_frame,
            text="➤",
            command=self.send_message,
            state=DISABLED,
            **self.styles.button_style
        )
        self.send_btn.pack(side=LEFT)

        # Microphone button
        self.mic_btn = Button(
            self.input_frame,
            text="🎤",
            command=self.record_and_send_audio,
            state=DISABLED,
            **self.styles.secondary_button_style
        )
        self.mic_btn.pack(side=LEFT, padx=5)

        
        # User list (right panel)
        self.user_frame = Frame(self.root, bg=self.styles.bg_medium, width=200)
        self.user_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")  # Make sure it spans both rows and uses nsew
        
        # Configure the column weight to ensure the user frame has a fixed width
        self.root.grid_columnconfigure(0, weight=1)  # Main content expands
        self.root.grid_columnconfigure(1, weight=0)  # User list stays fixed width
        
        self.user_list_label = Label(
            self.user_frame,
            text="ONLINE (0)",
            bg=self.styles.bg_medium,
            fg=self.styles.text_secondary,
            font=self.styles.font_bold,
            pady=10
        )
        self.user_list_label.pack(fill=X)
        
        self.user_listbox = Listbox(
            self.user_frame,
            bg=self.styles.bg_medium,
            fg=self.styles.text_primary,
            borderwidth=0,
            highlightthickness=0,
            font=self.styles.font_normal,
            selectbackground=self.styles.bg_light,
            width=15  # Set a fixed width for the listbox
        )
        self.user_listbox.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.user_listbox.bind("<Button-1>", self.handle_user_click)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def record_and_send_audio(self):
        try:
            duration = 5  # seconds
            fs = 44100  # Sample rate
            channels = 1  # Mono recording

            self.display_system_message("Recording audio for 5 seconds...")
            self.root.update_idletasks()  # Force UI update

            # Record audio
            audio = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype='int16')
            sd.wait()  # Wait until recording is finished

            # Save as .wav
            filename = os.path.join(self.file_dir, f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
            write(filename, fs, audio)

            # Send the file
            self.send_file_dialog_preselected(filename)

        except Exception as e:
            messagebox.showerror("Recording Error", f"Failed to record/send audio: {str(e)}")
            
    def send_file_dialog_preselected(self, filepath):
        try:
            basename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)

            self.display_system_message(f"Sending file {basename}...")
            self.root.update_idletasks()  # Force UI update

            msg_data = {
                "type": "FILE_METADATA",
                "filename": basename,
                "size": filesize
            }

            if self.whisper_target:
                msg_data["target"] = self.whisper_target

            # Send metadata
            self.client_socket.sendall(json.dumps(msg_data).encode('utf-8'))

            # Wait for acknowledgment with timeout
            self.client_socket.settimeout(5.0)
            ack_data = b''
            while True:
                chunk = self.client_socket.recv(1024)
                if not chunk:
                    raise ConnectionError("No response from server")
                ack_data += chunk
                try:
                    ack = json.loads(ack_data.decode('utf-8'))
                    if ack.get("status") != "ready":
                        raise Exception("Server not ready for file transfer")
                    break
                except json.JSONDecodeError:
                    continue

            # Send file data in chunks
            with open(filepath, 'rb') as f:
                while chunk := f.read(4096):
                    self.client_socket.sendall(chunk)

            self.display_system_message(f"{basename} sent successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send file: {str(e)}")
            self.disconnect()
        finally:
            self.client_socket.settimeout(None)  # Reset timeout

    def show_emoji_picker(self):
        # Check if emoji picker already exists and is open
        if hasattr(self, 'emoji_picker') and hasattr(self.emoji_picker, 'popup') and self.emoji_picker.popup.winfo_exists():
            self.emoji_picker.close()
            return
        
        # Create new emoji picker
        self.emoji_picker = EmojiPicker(self.input_frame, self.insert_emoji)

    def insert_emoji(self, emoji_char):
        self.message_entry.insert(END, emoji_char)
        self.message_entry.focus_set()
    
    def connect_to_server(self):
        server_ip = self.ip_entry.get()
        port = self.port_entry.get()
        nickname = self.nick_entry.get().strip()
        
        if not nickname:
            messagebox.showerror("Error", "Please enter a nickname")
            return
        
        if not port.isdigit():
            messagebox.showerror("Error", "Port must be a number")
            return
        
        port = int(port)
        
        try:
            # Close existing socket if any
            if hasattr(self, 'client_socket') and self.client_socket:
                try:
                    self.client_socket.close()
                except:
                    pass
            
            # Create new socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)  # Increased timeout
            
            # Connect to server
            self.client_socket.connect((server_ip, port))
            
            # Send nickname
            self.client_socket.sendall(json.dumps({
                "nickname": nickname
            }).encode('utf-8'))
            
            # Wait for response
            complete_data = b''
            while True:
                chunk = self.client_socket.recv(1024)
                if not chunk:
                    raise ConnectionError("No response from server")
                complete_data += chunk
                try:
                    # Try to parse the complete message
                    response = json.loads(complete_data.decode('utf-8'))
                    break  # If successful, exit
                except json.JSONDecodeError:
                    # Incomplete JSON, continue receiving data
                    continue
            
            if response.get('type') != 'CONNECTION_SUCCESS':
                raise ConnectionError(response.get('message', 'Connection rejected'))
            
            # Remove timeout for regular operation
            self.client_socket.settimeout(None)
            
            # Update UI
            self.connect_btn.config(state=DISABLED)
            self.disconnect_btn.config(state=NORMAL)
            self.send_btn.config(state=NORMAL)
            self.file_btn.config(state=NORMAL)
            self.mic_btn.config(state=NORMAL)
            self.ip_entry.config(state='readonly')
            self.port_entry.config(state='readonly')
            self.nick_entry.config(state='readonly')
            
            # Start receive thread
            self.receive_thread = threading.Thread(
                target=self.receive_messages,
                daemon=True
            )
            self.receive_thread.start()
            
            self.display_system_message(f"Connected as {nickname}")
            
        except socket.timeout:
            messagebox.showerror("Error", "Connection timed out")
            if hasattr(self, 'client_socket'):
                self.client_socket.close()
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Server not available")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
            if hasattr(self, 'client_socket'):
                self.client_socket.close()
    
    def disconnect(self):
        try:
            if hasattr(self, 'client_socket') and self.client_socket:
                try:
                    self.client_socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    self.client_socket.close()
                except:
                    pass
        except:
            pass
    
    # Reset UI
        self.connect_btn.config(state=NORMAL)
        self.disconnect_btn.config(state=DISABLED)
        self.send_btn.config(state=DISABLED)
        self.file_btn.config(state=DISABLED)
        self.mic_btn.config(state=DISABLED)
        self.ip_entry.config(state='normal')
        self.port_entry.config(state='normal')
        self.nick_entry.config(state='normal')
        self.whisper_target = None
        self.display_system_message("Disconnected from server")
        
    def handle_user_click(self, event):
        selection = self.user_listbox.curselection()
        if not selection:
            return
            
        selected_text = self.user_listbox.get(selection[0])
        if selected_text.startswith("→ "):
            target = selected_text[2:]
        else:
            target = selected_text
            
        if target == self.nick_entry.get():
            self.display_system_message("You cannot whisper to yourself")
            return
            
        if target == self.whisper_target:
            self.stop_whisper()
        else:
            self.start_whisper(target)
    
    def start_whisper(self, target):
        self.whisper_target = target
        self.display_system_message(f"Now whispering to {target} (click again to stop)")
        self.message_entry.config(bg=self.styles.accent, fg="white")
        self.message_entry.delete(0, END)
        self.message_entry.focus_set()
        
        if hasattr(self, 'clients'):
            user_list = [data['nickname'] for _, data in self.clients.items()]
            self.update_user_list(user_list)
        elif self.user_listbox.size() > 0:
            # If clients dict not available, get users from listbox
            user_list = [self.user_listbox.get(i).replace("→ ", "") for i in range(self.user_listbox.size())]
            self.update_user_list(user_list)

    def stop_whisper(self):
        if self.whisper_target:
            self.display_system_message(f"Stopped whispering to {self.whisper_target}")
            self.whisper_target = None
            self.message_entry.config(bg=self.styles.bg_input, fg=self.styles.text_primary)
            self.message_entry.delete(0, END)
            
            # Update user list to remove highlight
            if hasattr(self, 'clients'):
                user_list = [data['nickname'] for _, data in self.clients.items()]
                self.update_user_list(user_list)
            elif self.user_listbox.size() > 0:
                # If clients dict not available, get users from listbox
                user_list = [self.user_listbox.get(i).replace("→ ", "") for i in range(self.user_listbox.size())]
                self.update_user_list(user_list)
        
    def send_message(self, event=None):
        if not hasattr(self, 'client_socket') or self.client_socket.fileno() == -1:
            messagebox.showerror("Error", "Not connected to server")
            return
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        try:
            # Convert emoji shortcodes
            message = emoji.emojize(message, language='alias')
            
            if self.whisper_target:
                # Display the whisper message locally first
                self.display_chat_bubble(
                    "You",
                    message,
                    is_me=True,
                    is_whisper=True,
                    time=datetime.now().strftime("%H:%M")
                )
                
                # Send private message
                msg_data = {
                    "type": "WHISPER",
                    "target": self.whisper_target,
                    "message": message
                }
            else:
                # Send public message
                msg_data = {
                    "type": "TEXT_MESSAGE",
                    "message": message
                }
                # Public messages will be displayed when received back from server
            
            self.client_socket.sendall(json.dumps(msg_data).encode('utf-8'))
            self.message_entry.delete(0, END)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")
            self.disconnect()
        
    def send_file_dialog(self):
        if not hasattr(self, 'client_socket') or not self.client_socket:
            messagebox.showerror("Error", "Not connected to server")
            return
            
        # Check if socket is valid
        try:
            if self.client_socket.fileno() == -1:
                messagebox.showerror("Error", "Socket connection is closed")
                return
        except:
            messagebox.showerror("Error", "Invalid socket connection")
            return
        
        filename = filedialog.askopenfilename(title="Select file to share")
        if not filename:
            return
        
        try:
            # Ensure file exists and is accessible
            if not os.path.isfile(filename):
                messagebox.showerror("Error", f"Cannot access file: {filename}")
                return
                
            basename = os.path.basename(filename)
            filesize = os.path.getsize(filename)
            
            # Show sending message to user
            self.display_system_message(f"Sending file {basename}...")
            
            # Send metadata
            msg_data = {
                "type": "FILE_METADATA",
                "filename": basename,
                "size": filesize
            }
            
            if self.whisper_target:
                msg_data["target"] = self.whisper_target
            
            # First verify socket is still valid
            if not self.client_socket or self.client_socket.fileno() == -1:
                messagebox.showerror("Error", "Connection lost before sending")
                return
                
            self.client_socket.sendall(json.dumps(msg_data).encode('utf-8'))
            
            # Store original timeout
            original_timeout = None
            try:
                original_timeout = self.client_socket.gettimeout()
                
                # Wait for acknowledgment
                ack_data = b''
                while True:
                    try:
                        chunk = self.client_socket.recv(1024)
                        if not chunk:
                            raise ConnectionError("No response from server")
                    
                        ack_data += chunk
                        ack = json.loads(ack_data.decode('utf-8'))
                        break
                    except json.JSONDecodeError:
                        continue
                        
                if ack.get('status') != 'ready':
                    raise ConnectionError(ack.get('message', 'Server not ready'))
                
                # Send file data
                with open(filename, 'rb') as f:
                    bytes_sent = 0
                    while True:
                        chunk = f.read(4096)  # Smaller chunk size 
                        if not chunk:
                            break
                        # Check socket before each send
                        if not self.client_socket or self.client_socket.fileno() == -1:
                            raise ConnectionError("Connection lost during transfer")
                        self.client_socket.sendall(chunk)
                        bytes_sent += len(chunk)
                        
                        # Give UI a chance to update
                        self.root.update_idletasks()
                
                self.display_system_message(f"File {basename} sent successfully")
                
            except socket.timeout:
                messagebox.showerror("Error", "Server response timeout")
            except ConnectionError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"File transfer failed: {str(e)}")
            finally:
                # Restore original timeout if socket is still valid
                if self.client_socket and hasattr(self.client_socket, 'fileno'):
                    try:
                        if self.client_socket.fileno() != -1 and original_timeout is not None:
                            self.client_socket.settimeout(original_timeout)
                    except:
                        pass  # If setting timeout fails, don't crash
                        
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def download_file(self, filename):
        save_path = filedialog.asksaveasfilename(
            initialfile=filename,
            title=f"Save {filename}"
        )
        
        if not save_path:
            return
        
        try:
            # Show downloading message
            self.display_system_message(f"Downloading {filename}...")
            
            # Request file
            self.client_socket.sendall(json.dumps({
                "type": "FILE_REQUEST",
                "filename": filename
            }).encode('utf-8'))
            
            # Get file info with timeout
            self.client_socket.settimeout(5.0)
            file_data = b''
            while True:
                chunk = self.client_socket.recv(1024)
                if not chunk:
                    raise ConnectionError("Server disconnected")
                    
                file_data += chunk
                try:
                    file_info = json.loads(file_data.decode('utf-8'))
                    break
                except json.JSONDecodeError:
                    continue
                    
            if file_info.get('type') != 'FILE_START':
                raise ConnectionError("Invalid response from server")
            
            filesize = file_info['size']
            received = 0
            
            # Reset timeout for file transfer
            self.client_socket.settimeout(30.0)
            
            # Receive file data with progress updates
            with open(save_path, 'wb') as f:
                while received < filesize:
                    data = self.client_socket.recv(min(8192, filesize - received))
                    if not data:
                        raise ConnectionError("Transfer incomplete")
                    f.write(data)
                    received += len(data)
                    
                    # Update progress every 10%
                    if received % (filesize // 10 + 1) == 0 or received == filesize:
                        percent = int(received * 100 / filesize)
                        self.display_system_message(f"Downloading {filename}: {percent}%")
            
            self.display_system_message(f"Downloaded {filename} successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        finally:
            # Reset timeout to None after transfer
            self.client_socket.settimeout(None)
    
    def show_emoji_picker(self):
        if hasattr(self, 'emoji_picker') and hasattr(self.emoji_picker, 'popup') and self.emoji_picker.popup.winfo_exists():
            self.emoji_picker.close()
            return
        
        self.emoji_picker = EmojiPicker(self.input_frame, self.insert_emoji)
    
    def insert_emoji(self, emoji_char):
        self.message_entry.insert(END, emoji_char)
        self.message_entry.focus_set()
    
    def display_system_message(self, message):
        self.chat_display.config(state='normal')
        
        # Add some spacers to separate system message from user messages
        self.chat_display.insert(END, "\n", "system")
        
        # Create a frame for the system message
        system_frame = Frame(
            self.chat_display,
            bg=self.styles.bg_medium,
            padx=8,
            pady=4,
        )
        
        # Add the system message label
        Label(
            system_frame,
            text=f"[System] {message}",
            bg=self.styles.bg_medium,
            fg=self.styles.text_secondary,
            font=self.styles.font_small,
            wraplength=300,
            justify="center"
        ).pack()
        
        # Insert into chat centered
        self.chat_display.window_create(END, window=system_frame)
        self.chat_display.insert(END, "\n\n")
        
        # Center the frame
        system_frame.pack(anchor="center", padx=10, pady=3)
        
    # At the end of display_file_message and display_system_message
        self.chat_display.config(state='disabled')
        self.chat_display.update_idletasks()
        self.chat_display.yview_moveto(1.0)  # Force scroll to bottom
        

    def display_chat_bubble(self, sender, message, is_me=False, is_file=False, file_info=None, time=None, is_whisper=False):
        self.chat_display.config(state='normal')
        
        # Configure message style
        bubble_bg = self.styles.accent if is_me else self.styles.bg_light
        time_str = time if time else datetime.now().strftime("%H:%M")
        
        # Alignment settings
        alignment = "e" if is_me else "w"  # east for right, west for left
        
        # Create bubble frame
        bubble_frame = Frame(
            self.chat_display,
            bg=bubble_bg,
            padx=8,
            pady=6,
            bd=1,  # Small border
            highlightthickness=0,
            relief="solid"  # Make border visible
        )
        
        # Add sender name (except for own messages)
        if not is_me:
            Label(
                bubble_frame,
                text=sender,
                bg=bubble_bg,
                fg="#ffcc00" if is_whisper else self.styles.text_secondary,
                font=self.styles.font_small,
                anchor="w"
            ).pack(anchor="w", pady=(0, 2))
        
        if is_file:
            # File message UI
            icon = "📄" if not file_info['is_image'] else "🖼️"
            Label(
                bubble_frame,
                text=f"{icon} {file_info['name']}",
                bg=bubble_bg,
                fg="white" if is_me else self.styles.text_primary,
                font=self.styles.font_bold,
                anchor="w"
            ).pack(anchor="w")
            
            Label(
                bubble_frame,
                text=f"{file_info['size']} • {file_info['type']}",
                bg=bubble_bg,
                fg="white" if is_me else self.styles.text_secondary,
                font=self.styles.font_small,
                anchor="w"
            ).pack(anchor="w")
            
            if not is_me:  # Download button for received files
                Button(
                    bubble_frame,
                    text="Download",
                    command=lambda: self.download_file(file_info['name']),
                    **self.styles.secondary_button_style
                ).pack(anchor="w", pady=3)
        else:
            # Text message with whisper styling if needed
            text_color = "white" if is_me else self.styles.text_primary
            if is_whisper and not is_me:
                text_color = self.styles.accent
                
            Label(
                bubble_frame,
                text=message,
                bg=bubble_bg,
                fg=text_color,
                font=self.styles.font_normal,
                wraplength=280,
                justify="left",
                anchor="w"
            ).pack(anchor="w", padx=2, pady=2)
        
        # Timestamp with proper styling
        timestamp_frame = Frame(bubble_frame, bg=bubble_bg)
        timestamp_frame.pack(anchor="e", padx=2)
        
        # Fixed color values to match your requirements
        timestamp_color = "white" if is_me else self.styles.accent
        
        Label(
            timestamp_frame,
            text=time_str,
            bg=bubble_bg,
            fg=timestamp_color,
            font=self.styles.font_small
        ).pack(side="right")
        
        # Insert into chat with proper alignment
        self.chat_display.window_create("end", window=bubble_frame)
        self.chat_display.insert("end", "\n\n")
        
        # Set bubble anchor position
        bubble_frame.pack(anchor=alignment, padx=10, pady=3)
        
        # Fix scrolling - this is the critical change
        self.chat_display.config(state='disabled')
        self.chat_display.update_idletasks()
        self.chat_display.yview_moveto(1.0)  # Force scroll to bottom

    
    def display_file_message(self, filename, file_info):
        self.chat_display.config(state='normal')
        
        # Determine if this is a sent or received file
        is_me = file_info.get('sender', '') == "You" or file_info.get('sender', '') == self.nick_entry.get()
        
        # Create bubble frame with proper styling
        bubble_bg = self.styles.accent if is_me else self.styles.bg_light
        
        # Alignment settings
        alignment = "e" if is_me else "w"  # east for right, west for left
        
        # Create container frame
        container = Frame(
            self.chat_display,
            bg=bubble_bg,
            padx=8,
            pady=6,
            bd=1,
            highlightthickness=0,
            relief="solid"
        )
        
        # Add sender name for received files
        if not is_me:
            Label(
                container,
                text=file_info['sender'],
                bg=bubble_bg,
                fg=self.styles.text_secondary,
                font=self.styles.font_small,
                anchor="w"
            ).pack(anchor="w", pady=(0, 2))
        
        # File icon and name
        is_image = file_info.get('is_image', any(filename.lower().endswith(ext) for ext in ['.png','.jpg','.jpeg','.gif']))
        icon = "🖼️" if is_image else "📄"
        
        Label(
            container,
            text=f"{icon} {filename}",
            bg=bubble_bg,
            fg="white" if is_me else self.styles.text_primary,
            font=self.styles.font_bold,
            anchor="w"
        ).pack(anchor="w")
        
        # File info
        size_text = f"{file_info['size']} bytes"
        if file_info['size'] > 1024:
            size_text = f"{file_info['size'] // 1024} KB"
        if file_info['size'] > 1024 * 1024:
            size_text = f"{file_info['size'] // (1024 * 1024):.1f} MB"
            
        info_text = f"{size_text} • {file_info.get('type', 'File')}"
        if file_info.get('private'):
            info_text += " • [PRIVATE]"
            
        Label(
            container,
            text=info_text,
            bg=bubble_bg,
            fg="white" if is_me else self.styles.text_secondary,
            font=self.styles.font_small,
            anchor="w"
        ).pack(anchor="w")
        
        # Download button (only for received files)
        if not is_me:
            Button(
                container,
                text="Download",
                command=lambda f=filename: self.download_file(f),
                **self.styles.secondary_button_style
            ).pack(anchor="w", pady=3)
        
        # Time stamp with proper styling
        timestamp_frame = Frame(container, bg=bubble_bg)
        timestamp_frame.pack(anchor="e", padx=2)
        
        # Fixed color values to match your requirements
        timestamp_color = "white" if is_me else self.styles.accent
        
        Label(
            timestamp_frame,
            text=file_info.get('time', datetime.now().strftime("%H:%M")),
            bg=bubble_bg,
            fg=timestamp_color,
            font=self.styles.font_small
        ).pack(side="right")
        
        # Insert into chat
        self.chat_display.window_create(END, window=container)
        self.chat_display.insert(END, "\n\n")
        
        # Set container anchor position
        container.pack(anchor=alignment, padx=10, pady=3)
        
# At the end of display_file_message and display_system_message
        self.chat_display.config(state='disabled')
        self.chat_display.update_idletasks()
        self.chat_display.yview_moveto(1.0)  # Force scroll to bottom

    
    def update_user_list(self, users):
        self.user_listbox.delete(0, END)
        for user in sorted(users):
            # Highlight whisper target with a special prefix
            if user == self.whisper_target:
                self.user_listbox.insert(END, f"→ {user}")
            else:
                self.user_listbox.insert(END, user)
        
        # Update title with count
        self.user_list_label.config(text=f"ONLINE ({len(users)})")
        
    def receive_messages(self):
        buffer_size = 8192
        self.clients = {}  # Initialize clients dictionary
        accumulated_data = b''
        
        while True:
            try:
                chunk = self.client_socket.recv(buffer_size)
                if not chunk:
                    raise ConnectionError("Server disconnected")
                
                accumulated_data += chunk
                
                # Try to extract complete JSON messages
                while accumulated_data:
                    try:
                        # Try to decode the JSON
                        message = json.loads(accumulated_data.decode('utf-8'))
                        accumulated_data = b''  # Clear the buffer after successful parse
                        
                        # Process the message
                        if message['type'] == 'TEXT_MESSAGE':
                            is_me = (message['sender'] == self.nick_entry.get())
                            self.root.after(0, lambda m=message, me=is_me: self.display_chat_bubble(
                                m['sender'],
                                m['message'],
                                is_me=me,
                                time=m.get('time')
                            ))
                        elif message['type'] == 'WHISPER':
                            is_me = (message['sender'] == self.nick_entry.get())
                            self.root.after(0, lambda m=message, me=is_me: self.display_chat_bubble(
                                m['sender'],
                                m['message'],
                                is_me=me,
                                is_whisper=True,
                                time=m.get('time')
                            ))
                        elif message['type'] == 'FILE_AVAILABLE':
                            is_me = (message['sender'] == self.nick_entry.get())
                            self.root.after(0, lambda m=message, me=is_me: self.display_file_message(
                                m['filename'],
                                {
                                    "size": m['size'],
                                    "sender": m['sender'],
                                    "private": m.get('private', False),
                                    "time": m.get('time'),
                                    "is_image": any(m['filename'].lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']),
                                    "type": "Image" if any(m['filename'].lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']) else "Document",
                                    "name": m['filename']
                                }
                            ))
                        elif message['type'] == 'SYSTEM_MESSAGE':
                            self.root.after(0, lambda m=message: self.display_system_message(
                                m['message']
                            ))
                        elif message['type'] == 'USER_LIST':
                            if isinstance(message.get('users'), list):
                                # Store client list for user interaction
                                self.clients = {user: {"nickname": user} for user in message['users']}
                                self.root.after(0, lambda m=message: self.update_user_list(
                                    m['users']
                                ))
                        break  # Exit the while loop after processing a complete message
                        
                    except json.JSONDecodeError:
                        # If we can't decode yet, there might be more data coming
                        # Check if we have multiple messages concatenated
                        try:
                            # Find the end of the first JSON object
                            pos = accumulated_data.find(b'}') + 1
                            if pos > 0:
                                first_message = accumulated_data[:pos]
                                remaining_data = accumulated_data[pos:]
                                
                                message = json.loads(first_message.decode('utf-8'))
                                accumulated_data = remaining_data
                                
                                # Process the message (same logic as above)
                                # Duplicate the message processing logic here
                                if message['type'] == 'TEXT_MESSAGE':
                                    is_me = (message['sender'] == self.nick_entry.get())
                                    self.root.after(0, lambda m=message, me=is_me: self.display_chat_bubble(
                                        m['sender'],
                                        m['message'],
                                        is_me=me,
                                        time=m.get('time')
                                    ))
                                elif message['type'] == 'WHISPER':
                                    is_me = (message['sender'] == self.nick_entry.get())
                                    self.root.after(0, lambda m=message, me=is_me: self.display_chat_bubble(
                                        m['sender'],
                                        m['message'],
                                        is_me=me,
                                        is_whisper=True,
                                        time=m.get('time')
                                    ))
                                elif message['type'] == 'FILE_AVAILABLE':
                                    is_me = (message['sender'] == self.nick_entry.get())
                                    self.root.after(0, lambda m=message, me=is_me: self.display_file_message(
                                        m['filename'],
                                        {
                                            "size": m['size'],
                                            "sender": m['sender'],
                                            "private": m.get('private', False),
                                            "time": m.get('time'),
                                            "is_image": any(m['filename'].lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']),
                                            "type": "Image" if any(m['filename'].lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']) else "Document",
                                            "name": m['filename']
                                        }
                                    ))
                                elif message['type'] == 'SYSTEM_MESSAGE':
                                    self.root.after(0, lambda m=message: self.display_system_message(
                                        m['message']
                                    ))
                                elif message['type'] == 'USER_LIST':
                                    if isinstance(message.get('users'), list):
                                        # Store client list for user interaction
                                        self.clients = {user: {"nickname": user} for user in message['users']}
                                        self.root.after(0, lambda m=message: self.update_user_list(
                                            m['users']
                                        ))
                                continue  # Continue processing remaining data
                            else:
                                # No complete message yet
                                break
                        except (json.JSONDecodeError, ValueError):
                            # If still can't parse, wait for more data
                            break
            
            except (ConnectionError, socket.error) as e:
                print(f"Connection error: {e}")
                self.root.after(0, self.disconnect)
                break
            except Exception as e:
                print(f"Error in receive loop: {str(e)}")
        
    def on_closing(self):
        if hasattr(self, 'disconnect_btn') and self.disconnect_btn['state'] == NORMAL:
            self.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    ModernChatClient()


