import os
import sys
import socket
import threading
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
import pystray
from pystray import MenuItem as item
from tendo import singleton

# 1. ระบบป้องกันการเปิดซ้ำ (Single Instance)
try:
    me = singleton.SingleInstance()
except:
    sys.exit()

class HHTBridgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows 11 to HHT Bridge")
        self.geometry("500x400")
        self.protocol('WM_DELETE_WINDOW', self.hide_window) # ปิดแล้วไปที่ Tray

        # UI Setup
        self.label = ctk.CTkLabel(self, text="HHT Connection Status: Waiting...", font=("Segoe UI", 16))
        self.label.pack(pady=20)

        self.btn_transfer = ctk.CTkButton(self, text="Transfer File to HHT", command=self.transfer_file)
        self.btn_transfer.pack(pady=10)

        self.log_box = ctk.CTkTextbox(self, width=450, height=200)
        self.log_box.pack(pady=10)

        # Start TCP Server for 3rd Party
        threading.Thread(target=self.start_socket_server, daemon=True).start()

    def start_socket_server(self):
        """เปิด Port สำหรับให้โปรแกรมอื่นส่งข้อมูลผ่าน"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 9999)) # Port 9999
        server.listen(5)
        self.update_log("Interface Port 9999 started.")
        while True:
            conn, addr = server.accept()
            data = conn.recv(1024)
            if data:
                self.update_log(f"Received from 3rd Party: {data.decode()}")
                # TODO: ส่งข้อมูลต่อไปยัง Windows CE ผ่าน RAPI
            conn.close()

    def transfer_file(self):
        # Placeholder สำหรับการโยนไฟล์ผ่าน RAPI.dll
        self.update_log("Action: Attempting to transfer file...")
        messagebox.showinfo("Transfer", "RAPI Connection Required for WinCE")

    def update_log(self, message):
        self.log_box.insert("end", f"{message}\n")

    def hide_window(self):
        self.withdraw()

    def show_window(self):
        self.deiconify()

# --- System Tray Management ---
def quit_app(icon, item):
    icon.stop()
    sys.exit()

def setup_tray(app):
    image = Image.new('RGB', (64, 64), color=(73, 109, 137)) # สร้าง Icon จำลอง
    menu = (item('Open', lambda: app.show_window()), item('Quit', quit_app))
    icon = pystray.Icon("HHTBridge", image, "HHT Bridge Tool", menu)
    icon.run_detach()

if __name__ == "__main__":
    app = HHTBridgeApp()
    setup_tray(app)
    app.mainloop()
