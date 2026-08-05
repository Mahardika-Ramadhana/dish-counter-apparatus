import tkinter as tk
from PIL import Image, ImageTk
import config
from typing import Callable

class DishCounterGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Dish Counter Apparatus")
        self.root.configure(bg="#f0f0f0")
        
        self.weight_var = tk.StringVar(value="Berat: 0 g")
        self.total_price_var = tk.StringVar(value="Total: Rp0")
        self.detected_items_var = tk.StringVar(value="Silakan letakkan piring dan tekan DETEKSI...")
        self.wifi_var = tk.StringVar(value="WiFi: Disconnected")
        
        self._setup_ui()
        self.on_detect: Callable = None
        
    def _setup_ui(self):
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", lambda e: self.root.attributes('-fullscreen', False))
        self.root.configure(bg="black")
        
        # Callbacks
        self.on_detect = None
        self.on_wifi_click = None
        self.on_paid = None
        
        # 5-inch simulator container
        self.sim_frame = tk.Frame(self.root, bg="#f4f6f7", width=800, height=480)
        self.sim_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.sim_frame.pack_propagate(False)
        
        # Main Layout (Fullscreen inside sim_frame)
        self.main_frame = tk.Frame(self.sim_frame, bg="#f4f6f7")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.cam_frame = tk.Label(self.main_frame, bg="black", text="Kamera...", fg="white", font=("Helvetica", 12))
        self.cam_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = tk.Frame(self.main_frame, bg="#f0f0f0", width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)
        
        self.wifi_lbl = tk.Label(right_frame, textvariable=self.wifi_var, font=("Helvetica", 10, "bold"), bg="#f0f0f0", fg="#2980b9", anchor="e", cursor="hand2")
        self.wifi_lbl.pack(fill=tk.X, pady=(0, 2))
        self.wifi_lbl.bind("<Button-1>", lambda e: self.on_wifi_click() if self.on_wifi_click else None)
        
        # IP Label tiny at the top right
        self.ip_lbl = tk.Label(right_frame, text="Web: -", font=("Helvetica", 10), bg="#f0f0f0", fg="#7f8c8d", anchor="e", cursor="hand2")
        self.ip_lbl.pack(fill=tk.X, pady=(0, 2))
        self.ip_lbl.bind("<Button-1>", lambda e: self.on_dashboard_click() if hasattr(self, 'on_dashboard_click') and self.on_dashboard_click else None)
        
        weight_lbl = tk.Label(right_frame, textvariable=self.weight_var, font=("Helvetica", 16, "bold"), bg="white", fg="#2980b9", relief=tk.RIDGE, bd=2, pady=5)
        weight_lbl.pack(fill=tk.X, pady=(0, 5))
        
        self.items_lbl = tk.Label(right_frame, textvariable=self.detected_items_var, font=("Helvetica", 11), bg="white", justify=tk.LEFT, anchor="nw", relief=tk.RIDGE, bd=2, padx=5, pady=5)
        self.items_lbl.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        
        price_lbl = tk.Label(right_frame, textvariable=self.total_price_var, font=("Helvetica", 18, "bold"), bg="#f1c40f", fg="black", relief=tk.RIDGE, bd=2, pady=8)
        price_lbl.pack(fill=tk.X, pady=(0, 5))
        
        btn_frame = tk.Frame(right_frame, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.btn_detect = tk.Button(btn_frame, text="DETEKSI", font=("Helvetica", 14, "bold"), bg="#e74c3c", fg="white", height=2, command=self._handle_detect)
        self.btn_detect.pack(fill=tk.X)
        
    def update_camera_preview(self, frame_rgb):
        if frame_rgb is not None:
            img = Image.fromarray(frame_rgb)
            img = img.resize((480, 360), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.cam_frame.imgtk = imgtk
            self.cam_frame.configure(image=imgtk, text="")
            
    def update_info(self, weight: float, detections: list, total_price: int, state: str = 'IDLE', val_items=None, val_total=0, is_auto=False):
        if val_items is None:
            val_items = []
        if state == 'IDLE':
            self.weight_var.set("Berat: - g (Tekan Tombol di Bawah)")
        else:
            self.weight_var.set(f"Berat: {weight:.1f} g")
        
        if state == 'VALIDATION':
            item_text = "MENUNGGU VALIDASI PENJUAL:\n"
            for det in val_items:
                if 'harga' in det:
                    item_text += f"• {det['class_name']} - Rp{det['harga']:,}\n"
                else:
                    item_text += f"• {det['class_name']}\n"
            self.items_lbl.configure(bg="#fff3cd") # Yellow warning
            self.total_price_var.set("Total: Menghitung...")
            self.btn_detect.configure(state="disabled", text="MENUNGGU VALIDASI...")

            
        elif state == 'PAYMENT':
            item_text = "RINCIAN PEMBAYARAN:\n"
            for det in val_items:
                if 'harga' in det:
                    item_text += f"• {det['class_name']} - Rp{det['harga']:,}\n"
                else:
                    item_text += f"• {det['class_name']}\n"
            item_text += "\nSilakan scan QRIS di bawah ini."
            self.items_lbl.configure(bg="#e8f8f5") # light green
            self.total_price_var.set(f"Total: Rp{val_total:,}")
            
            if is_auto:
                self.btn_detect.configure(state="normal", text="SAYA SUDAH BAYAR", bg="#3498db")
            else:
                self.btn_detect.configure(state="disabled", text="MENUNGGU KONFIRMASI...", bg="#95a5a6")
            
            # Generate Real Dynamic QRIS
            import qrcode
            from qris import generate_dynamic_qris
            
            # QRIS Asli dari Warteg DICA
            static_qris_base = "00020101021126610014COM.GO-JEK.WWW01189360091439584610540210G9584610540303UMI51440014ID.CO.QRIS.WWW0215ID10265563222400303UMI5204581253033605802ID5923DICA, Makanan & Minuman6007CIREBON61054517162070703A01630459A4"
            
            # Ubah menjadi dinamis dengan harga (val_total)
            if val_total > 0:
                dynamic_payload = generate_dynamic_qris(static_qris_base, val_total)
            else:
                dynamic_payload = static_qris_base
            
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(dynamic_payload)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").resize((360, 360))
            
            qris_tk = ImageTk.PhotoImage(image=img)
            self.cam_frame.imgtk = qris_tk
            self.cam_frame.configure(image=qris_tk, bg="white")
            
        elif state == 'NEEDS_CALIBRATION':
            item_text = "SISTEM TERKUNCI.\n\nSesuai SOP, silakan taruh piring kosong\nlalu tekan 'Kalibrasi Timbangan (Tare)'\ndari Dashboard HP Penjual."
            self.items_lbl.configure(bg="#f8d7da") # Light red
            self.total_price_var.set("Total: Rp0")
            self.btn_detect.configure(state="disabled", text="MENUNGGU KALIBRASI...", bg="#95a5a6")
            
        else: # IDLE
            item_text = "Siap mendeteksi.\nSilakan letakkan piring beserta lauk."
            self.items_lbl.configure(bg="white")
            self.total_price_var.set("Total: Rp0")
            self.btn_detect.configure(state="normal", text="DETEKSI & HITUNG", bg="#e74c3c")
        self.detected_items_var.set(item_text)
        
    def _handle_detect(self):
        btn_text = self.btn_detect.cget('text')
        if btn_text == "SAYA SUDAH BAYAR":
            if self.on_paid:
                self.on_paid()
        else:
            if self.on_detect:
                self.on_detect()

    def show_receipt(self, total: int):
        self.detected_items_var.set(f"PEMBAYARAN BERHASIL!\n\nTerima kasih.\nTotal Dibayar: Rp{total:,}")
        self.items_lbl.configure(bg="#2ecc71") # Green success
        self.total_price_var.set("LUNAS")
        self.btn_detect.configure(state="disabled", text="LUNAS")
