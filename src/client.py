'''
CS 3700 - Networking & Distributed Computing - Fall 2024
Instructor: Thyago Mota
Student(s):
Description: Project 1 - Multiuser Chat: Client
'''
from queue import Queue
from socket import *
from struct import pack
from datetime import datetime
import tkinter as tk
from tkinter import *
from tkinter import messagebox, font, scrolledtext, ttk
from threading import Thread, Semaphore
import sys

# "constants"
MCAST_ADDR  = '224.1.1.1'
MCAST_PORT  = 2241
SERVER_PORT = 4321
BUFFER      = 1024
GEOMETRY    = '570x400'

# the semaphore!
s = Semaphore(1)

class Window(Tk):
    def __init__(self, server_addr):
        super().__init__()
        self.help_text = """
        ## Available Commands ##:

        • help, display this window
        • login, log in with a username    
        • list, show users logged in 
        • exit, leave the chat
        • msg, sends a message to the server 

        Welcome, your first message 
        will be your username
        """
        self.after(100, lambda: self.popup("Help", self.help_text))
        self.username = None
        self.logged_in = False
        self.message_queue = Queue()  #using a queue for thread-safe communication

        self.socket = socket(AF_INET, SOCK_DGRAM)

        self.server_addr = server_addr       

        self.title("UDP Chat")
        self.geometry(GEOMETRY)
        self.resizable(0,0)
        self.text_box = Text(self)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=9)

        self.label = Label(text='Message:')
        self.label.grid(column=0, row=0, sticky=tk.E)

        self.entry = Entry()
        self.entry.grid(column=1, row=0, sticky=tk.EW)
        self.entry.bind('<Return>', self.enter)

        self.text = Text(height=10, bg='black', fg='white')
        self.text.tag_configure("green", foreground="green")
        self.text.tag_configure("blue", foreground="blue")
        self.text.grid(column=0, row=1, columnspan=2, sticky=tk.NSEW)

        self.after(100, self.check_queue)
     
        self.clear_button = Button(self, text="Clear Messages", command=self.clear_messages) #button to clear messages
        self.clear_button.grid(column=1, row=2, sticky=tk.E, pady=5)

    def clear_messages(self):
        self.text.delete('1.0', END)

    def popup(self, title, message): #shows custom messagebox
        dialog = Toplevel(self)
        dialog.title("Help")
        dialog.geometry("570x400")
        
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)
       
        text = scrolledtext.ScrolledText(dialog, wrap=WORD, font=("Courier", 15))
        text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        text.insert(END, message)
        text.config(state=DISABLED)

        ok_button = Button(dialog, text="OK", command=dialog.destroy)
        ok_button.grid(row=1, column=0, pady=10)

        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
    
           

    def check_queue(self): #checks queue every 100ms and updates GUI
        while not self.message_queue.empty():
            msg = self.message_queue.get()
            self.update(msg)
        self.after(100, self.check_queue)

   
    def enter(self, event):
        message = self.entry.get()
        self.update(f"{self.username}|{message}")
        if message == "help,":
            self.popup("Help", self.help_text)

        if not self.logged_in:
            self.username = message
            self.logged_in = True
            self.socket.sendto(f"login,{self.username}".encode(), (self.server_addr, SERVER_PORT))
            self.message_queue.put(f"Logged in as: {self.username}")
            self.entry.delete(0, 'end')
        else:
            self.socket.sendto(f"{message}".encode(), (self.server_addr, SERVER_PORT))
            self.entry.delete(0, 'end')

    
    def update(self, msg):
        s.acquire()
        try:
            if self.username and msg.startswith(self.username):
                parts = msg.split("|", 1)
                if len(parts) == 2:
                    username, content = parts
                    self.text.insert(END, username, "green")
                    self.text.insert(END, f" | -> {content}\n")
                else:
                    self.text.insert(END, f"{msg}\n")
            elif msg.count('|') == 2:
                parts = msg.split('|')
                if len(parts) == 3:
                    address, message, username = parts
                    self.text.insert(END, f"{address.strip()}", "blue")
                    self.text.insert(END, f" | {message.strip()} |")
                    self.text.insert(END, f" {username.strip()}\n", "green")
            else:
                self.text.insert(END, f"{msg}\n")

            self.text.see(END)
        finally:
            s.release()

    def exit(self):
        self.socket.close()
        self.destroy()
        self.update("Connection closed, restart containers to communicate")


class FromServerThread(Thread): 

    def __init__(self, window): 
        Thread.__init__(self)

        # TODO #10 save thendow reference in an instance variable 
        self.window = window
    
        self.server_socket = socket(AF_INET, SOCK_DGRAM) #creates UDP socket
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) #allows socket to bind to address in time_wait
        self.server_socket.bind(('', MCAST_PORT)) #binds to all available addresses & mcast port

        # formats MCAST_ADDR to a network format
        group = inet_aton(MCAST_ADDR) 
        # formats the multicast group into a multicast request structure (mreq)
        mreq = pack('4sL', group, INADDR_ANY)
       
        try:
            self.server_socket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
            print("Joined multicast group")
        except Exception as e:
            print(f"Error joining multicast group: {e}")


    # TODO #11 read from the socket and update the window's text box
    def run(self): 
        while True: 
            try:
                data, addr = self.server_socket.recvfrom(BUFFER) #places received messages into check_queue
                server_msg = data.decode('utf-8')
                self.window.message_queue.put(server_msg)
                
            except Exception as e:
                print(f"error receiving data: {e}")
                break
            
if __name__ == '__main__': 
    if len(sys.argv) <= 1: 
        print(f'Use: {sys.argv[0]} server_address')
        sys.exit(1)
    server_addr = sys.argv[1].lower()

    window = Window(server_addr)
    from_server_thread = FromServerThread(window)
    from_server_thread.daemon = True
    from_server_thread.start()
    window.protocol("WM_DELETE_WINDOW", window.exit)
    window.mainloop()
