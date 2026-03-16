import os
import sys
import socket
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from tendo import singleton

# ==========================================
# 1. ระบบป้องกันการเปิดโปรแกรมซ้ำ (Single Instance)
# ==========================================
try:
    me = singleton.SingleInstance()
except:
    # ถ้ามีการรันอยู่แล้ว โปรแกรมจะจบการทำงานทันที
    sys.exit()

class HHTBridgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # การตั้งค่าหน้าต่างหลัก
        self.title("FTH Support - HHT Bridge v1.0")
        self.geometry("600x450")
        self.protocol('WM_DELETE_WINDOW', self.hide_window) # ปิด X แล้วซ่อนไปที่ Tray

        # --- UI Layout ---
        self.grid_columnconfigure(0, weight=1)
        
        self.label_status = ctk.CTkLabel(self, text="Status: Waiting for HHT...", font=("Segoe UI", 18, "bold"))
        self.label_status.pack(pady=(20, 10))

        # ปุ่มกด
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10, padx=20, fill="x")

        self.btn_transfer = ctk.CTkButton(self.btn_frame, text="Send File to HHT", command=self.upload_file)
        self.btn_transfer.grid(row=0, column=0, padx=10, pady=10)

        self.btn_sync = ctk.CTkButton(self.btn_frame, text="Sync Photos", fg_color="green", command=self.sync_photos)
        self.btn_sync.grid(row=0, column=1, padx=10, pady=10)

        # Log Box
        self.log_box = ctk.CTkTextbox(self, width=550, height=200)
        self.log_box.pack(pady=10, padx=20)
        self.update_log("System Started. Ready for interface.")

        # --- Backend Services ---
        # เริ่มต้น TCP Server บน Port 9999 เพื่อรองรับ 3rd Party App
        threading.Thread(target=self.start_socket_server, daemon=True).start()

    # ==========================================
    # 2. ฟังก์ชันจัดการหน้าต่าง และ System Tray
    # ==========================================
    def hide_window(self):
        self.withdraw() # ซ่อนหน้าต่าง

    def show_window(self):
        self.deiconify() # เรียกหน้าต่างกลับมา
        self.focus()

    def update_log(self, message):
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")

    # ==========================================
    # 3. Port Interface (TCP Server)
    # ==========================================
    def start_socket_server(self):
        """เปิด Port 9999 เพื่อรอรับคำสั่งจาก Application อื่นๆ"""
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('127.0.0.1', 9999))
            server.listen(5)
            self.update_log("Interface Port 9999 is now OPEN.")
            
            while True:
                conn, addr = server.accept()
                data = conn.recv(1024).decode('utf-8')
                if data:
                    self.update_log(f"Received Command: {data}")
                    # ส่วนนี้คือจุดที่จะส่งคำสั่งต่อไปยัง Windows CE (RAPI)
                conn.close()
        except Exception as e:
            self.update_log(f"Socket Error: {str(e)}")

    # ==========================================
    # 4. HHT Operations (Placeholders)
    # ==========================================
    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.update_log(f"Preparing to send: {os.path.basename(file_path)}")
            # TODO: ใส่คำสั่ง CeWriteFile (RAPI) ที่นี่
            messagebox.showinfo("HHT Bridge", "Connecting to Windows CE via RAPI...")

    def sync_photos(self):
        self.update_log("Scanning HHT for new photos...")
        # TODO: ใส่คำสั่ง CeReadFile (RAPI) ที่นี่

# ==========================================
# 5. System Tray & Application Start
# ==========================================
def create_image():
    """สร้าง Icon จำลอง (สี่เหลี่ยมสีฟ้า) กรณีไม่มีไฟล์ไอคอนจริง"""
    width, height = 64, 64
    image = Image.new('RGB', (width, height), (30, 144, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=(255, 255, 255))
    return image

def quit_app(icon, item, app):
    icon.stop()
    app.quit()
    sys.exit()

def setup_tray(app):
    menu = (
        item('Open Bridge', lambda: app.show_window()),
        item('Quit', lambda icon, item: quit_app(icon, item, app))
    )
    icon = pystray.Icon("HHTBridge", create_image(), "FTH HHT Bridge", menu)
    
    # รัน Tray Icon แยกเป็น Thread เพื่อไม่ให้ไปขัดขวางหน้าต่างหลัก
    threading.Thread(target=icon.run, daemon=True).start()

if __name__ == "__main__":
    app = HHTBridgeApp()
    setup_tray(app)
    app.mainloop()
