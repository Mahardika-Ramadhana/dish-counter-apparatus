import tkinter as tk
import time
import subprocess
import threading
import queue
from tkinter import messagebox
from camera import CameraManager
from loadcell import LoadCell
from detector import ObjectDetector
from database import Database
from gui import DishCounterGUI
from web_server import start_web_server
from logger import get_logger
import config
import cv2

logger = get_logger("MainApp")

try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logger.warning("gpiozero tidak ditemukan. Tombol fisik GPIO tidak aktif.")
except Exception as e:
    GPIO_AVAILABLE = False
    logger.error(f"Peringatan GPIO: {e}")

class App:
    def __init__(self, root):
        self.root = root
        
        logger.info("Menginisialisasi sistem...")
        self.db = Database()
        self.db.init_db()
        
        self.camera_manager = CameraManager()
        self.camera_manager.init_cameras()
        
        self.loadcell = LoadCell()
        self.loadcell.init_loadcell()
        
        self.detector = ObjectDetector()
        self.detector.load_model()
        
        self.gui = DishCounterGUI(self.root)
        
        self.gui.on_detect = self.trigger_detection
        self.gui.on_wifi_click = self.open_wifi_manager
        self.gui.on_dashboard_click = self.show_qr_window_if_connected
        self.gui.on_paid = self.konfirmasi_pembayaran_via_web
        
        self.btn_fisik = None
        if GPIO_AVAILABLE:
            try:
                self.btn_fisik = Button(config.PIN_TOMBOL, pull_up=True)
                self.btn_fisik.when_pressed = self.trigger_detection
                logger.info("Tombol fisik GPIO berhasil diinisialisasi.")
            except Exception as e:
                logger.error(f"Gagal inisialisasi tombol GPIO: {e}")
                
        self.current_detections = []
        self.current_total_price = 0
        self.current_weight = 0.0
        self.latest_frame_rgb = None
        
        self.transaction_state = 'NEEDS_CALIBRATION' # NEEDS_CALIBRATION, IDLE, VALIDATION, PAYMENT
        self.showing_dashboard_qr = False
        self.validated_items = []
        self.validated_total = 0
        self.last_drawn_frame_bgr = None
        self.auto_validate = False
        
        self.running = True
        self.frame_queue = queue.Queue(maxsize=1)
        self.trigger_detect_event = threading.Event()
        
        logger.info("Memulai pemrosesan paralel (Threading)...")
        self.cam_thread = threading.Thread(target=self.camera_task, daemon=True)
        self.ai_thread = threading.Thread(target=self.ai_task, daemon=True)
        self.sensor_thread = threading.Thread(target=self.sensor_task, daemon=True)
        
        self.cam_thread.start()
        self.ai_thread.start()
        self.sensor_thread.start()
        
        # Mulai Web Server Penjual
        logger.info("Memulai Web Server Penjual di background...")
        self.web_thread = threading.Thread(target=start_web_server, args=(self,), daemon=True)
        self.web_thread.start()
        
        # Start loops
        self.update_ip_display()
        self.root.after(30, self.update_gui_loop)
        
        # Selalu tampilkan Pengaturan WiFi di awal agar penjual bisa konfigurasi
        self.root.after(1000, self.open_wifi_manager)
        
    def camera_task(self):
        while self.running:
            frame_atas = self.camera_manager.capture_frame(config.CAMERA_IDS[0])
            frame_samping = None
            if len(config.CAMERA_IDS) > 1:
                frame_samping = self.camera_manager.capture_frame(config.CAMERA_IDS[1])
                
            if frame_atas is not None:
                display_frame = frame_atas.copy()
                if frame_samping is not None:
                    try:
                        h, w = display_frame.shape[:2]
                        pip_w, pip_h = w // 3, h // 3
                        pip_img = cv2.resize(frame_samping, (pip_w, pip_h))
                        # Tampilkan di pojok kanan bawah
                        display_frame[h-pip_h:h, w-pip_w:w] = pip_img
                        # Tambahkan border dan teks
                        cv2.rectangle(display_frame, (w-pip_w, h-pip_h), (w, h), (255,255,255), 2)
                        cv2.putText(display_frame, "KAMERA SAMPING", (w-pip_w + 5, h-pip_h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
                    except Exception as e:
                        print("Gagal membuat PiP kamera:", e)
                        
                self.latest_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                
                if not self.frame_queue.empty():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                self.frame_queue.put((frame_atas, frame_samping))
            time.sleep(0.03)
            
    def trigger_detection(self):
        if self.transaction_state == 'IDLE':
            self.transaction_state = 'PROCESSING'
            self.gui.update_info(self.current_weight, [], 0, 'VALIDATION', [], 0)
            self.trigger_detect_event.set()

    def ai_task(self):
        while self.running:
            if not self.trigger_detect_event.wait(timeout=0.1):
                continue
                
            self.trigger_detect_event.clear()
            
            try:
                frames = self.frame_queue.get(timeout=0.5)
                frame_atas, frame_samping = frames
                
                self.last_raw_frame_bgr = frame_atas.copy() if frame_atas is not None else None
                
                det_atas = self.detector.detect(frame_atas)
                atas_annotated = self.detector.last_annotated_frame
                
                det_samping = self.detector.detect(frame_samping) if frame_samping is not None else []
                samping_annotated = self.detector.last_annotated_frame
                
                final_detections = self.detector.consolidate_max_count(det_atas, det_samping)
                
                # (Logika kalkulasi porsi Nasi berdasarkan Loadcell dihapus karena Purwarupa fokus pada visi AI murni)
                total_price = sum([config.HARGA.get(d['class_name'], 0) for d in final_detections])
                
                # Masukkan harga ke dict agar bisa ditampilkan di UI
                for d in final_detections:
                    d['harga'] = config.HARGA.get(d['class_name'], 0)
                self.current_detections = final_detections
                self.current_total_price = total_price
                
                # Simpan frame untuk penjual
                if atas_annotated is not None:
                    draw_frame = atas_annotated
                else:
                    draw_frame = frame_atas.copy() if frame_atas is not None else np.zeros((480, 640, 3), dtype=np.uint8)
                    # Hapus fitur menggambar kotak hijau secara manual
                self.last_drawn_frame_bgr = draw_frame
                    
                if self.last_drawn_frame_bgr is not None and frame_samping is not None:
                    # PiP untuk AI frame (jika kamera samping ada)
                    try:
                        h, w = self.last_drawn_frame_bgr.shape[:2]
                        pip_w, pip_h = w // 3, h // 3
                        
                        samping_display = samping_annotated if samping_annotated is not None else frame_samping
                        
                        pip_img = cv2.resize(samping_display, (pip_w, pip_h))
                        self.last_drawn_frame_bgr[h-pip_h:h, w-pip_w:w] = pip_img
                        cv2.rectangle(self.last_drawn_frame_bgr, (w-pip_w, h-pip_h), (w, h), (0, 255, 0), 2)
                        cv2.putText(self.last_drawn_frame_bgr, "KAMERA SAMPING", (w-pip_w + 5, h-pip_h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
                    except Exception:
                        pass
                
                # Update GUI states:
                if self.auto_validate:
                    self.validated_items = final_detections
                    self.validated_total = total_price
                    self.transaction_state = 'PAYMENT'
                    logger.info("Auto-validasi aktif, transaksi otomatis dilanjutkan ke pembayaran.")
                else:
                    self.transaction_state = 'VALIDATION'
                
            except queue.Empty:
                if self.transaction_state == 'PROCESSING':
                    self.transaction_state = 'IDLE'
                    logger.error("Kamera tidak merespons (queue kosong). Deteksi dibatalkan.")
            except Exception as e:
                logger.error(f"Error pada saat deteksi AI: {e}")
                if self.transaction_state == 'PROCESSING':
                    self.transaction_state = 'IDLE'
                
    def sensor_task(self):
        while self.running:
            try:
                self.current_weight = self.loadcell.read_weight()
            except Exception as e:
                logger.error(f"Error membaca Loadcell: {e}")
                time.sleep(1) # Hindari spam error
            
    def update_gui_loop(self):
        if self.showing_dashboard_qr:
            if self.running:
                self.root.after(30, self.update_gui_loop)
            return
            
        if self.transaction_state == 'PROCESSING' and self.latest_frame_rgb is not None:
            draw_frame = self.latest_frame_rgb.copy()
            # Overlay loading text
            cv2.putText(draw_frame, "MEMPROSES AI...", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 4)
            self.gui.update_camera_preview(draw_frame)
        # Tampilkan segmentation mask jika sedang dalam status VALIDATION atau PAYMENT
        elif self.transaction_state in ['VALIDATION', 'PAYMENT'] and self.last_drawn_frame_bgr is not None:
            if self.transaction_state == 'VALIDATION':
                draw_frame_rgb = cv2.cvtColor(self.last_drawn_frame_bgr, cv2.COLOR_BGR2RGB)
                self.gui.update_camera_preview(draw_frame_rgb)
            # Jika PAYMENT, GUI (update_info) sudah menggambar QRIS di cam_frame, jadi JANGAN timpa dengan kamera.
        elif self.transaction_state == 'IDLE':
            if self.latest_frame_rgb is not None:
                # Mode IDLE: tampilkan kamera real-time tanpa bounding box
                self.gui.update_camera_preview(self.latest_frame_rgb)
            else:
                # FIX: Jika kamera mati/None, timpa sisa QRIS dengan layar peringatan hitam
                warn_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(warn_frame, "KAMERA MATI / TIDAK TERDETEKSI", (40, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                self.gui.update_camera_preview(warn_frame)
            
        self.gui.update_info(
            weight=self.current_weight, 
            detections=self.current_detections, 
            total_price=self.current_total_price, 
            state=self.transaction_state,
            val_items=self.validated_items,
            val_total=self.validated_total,
            is_auto=self.auto_validate
        )
        
        if self.running:
            self.root.after(30, self.update_gui_loop)
            
    def validasi_via_web(self, validated_items, validated_total):
        self.validated_items = validated_items
        self.validated_total = validated_total
        self.transaction_state = 'PAYMENT'
        logger.info(f"Validasi penjual selesai. Total final: Rp{validated_total}")

    def konfirmasi_pembayaran_via_web(self):
        if self.transaction_state != 'PAYMENT':
            return
            
        logger.info(f"Pembayaran via Web diterima senilai Rp{self.validated_total}.")
        self.db.save_transaction(self.validated_items, self.validated_total)
        
        self.gui.show_receipt(self.validated_total)
        
        self.current_detections = []
        self.current_total_price = 0
        self.validated_items = []
        self.validated_total = 0
        
        self.transaction_state = 'IDLE'
        self.last_drawn_frame_bgr = None
        
        # Kembalikan layar ke kondisi awal setelah 5 detik
        def reset_ui():
            self.gui.update_info(self.current_weight, [], 0, 'IDLE', [], 0)
        self.root.after(5000, reset_ui)
        
    def update_ip_display(self):
        from wifi_manager import get_current_ip, get_current_ssid
        ip = get_current_ip()
        self.gui.ip_lbl.config(text=f"Akses Penjual: http://{ip}:5000")
        
        if ip != "127.0.0.1":
            ssid = get_current_ssid()
            if ssid:
                self.gui.wifi_var.set(f"WiFi: {ssid}")
            else:
                self.gui.wifi_var.set("WiFi: Terhubung")
        else:
            self.gui.wifi_var.set("WiFi: Terputus")
            
        # Perbarui secara berkala jika IP berubah (misalnya baru connect)
        if self.running:
            self.root.after(10000, self.update_ip_display)

    def open_wifi_manager(self):
        from wifi_manager import scan_wifi, connect_wifi
        import tkinter as tk
        from tkinter import messagebox
        
        # Menggunakan Frame sebagai overlay layar utama, bukan popup Toplevel
        win = tk.Frame(self.root, bg="#ecf0f1")
        win.place(relx=0, rely=0, relwidth=1, relheight=1)
        win.tkraise() # Pastikan berada di paling atas
        
        tk.Label(win, text="Pilih Hotspot HP Penjual:", font=("Helvetica", 14, "bold"), bg="#ecf0f1").pack(pady=(15,5))
        
        status_lbl = tk.Label(win, text="Memindai jaringan WiFi...", font=("Helvetica", 10), bg="#ecf0f1", fg="#7f8c8d")
        status_lbl.pack(pady=2)
        
        frame_list = tk.Frame(win)
        frame_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame_list, font=("Helvetica", 12), yscrollcommand=scrollbar.set, selectbackground="#3498db")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        networks_cache = []
        
        def refresh_networks():
            if not win.winfo_exists():
                return
            status_lbl.config(text="Sedang memindai ulang...")
            
            result_container = {}
            
            def scan_thread():
                new_networks = scan_wifi()
                result_container['result'] = new_networks
                
            threading.Thread(target=scan_thread, daemon=True).start()
            
            def check_result():
                if not win.winfo_exists():
                    return
                if 'result' in result_container:
                    new_networks = result_container['result']
                    nonlocal networks_cache
                    # Hanya update jika list berubah untuk mencegah kedip (flickering)
                    if networks_cache != new_networks:
                        networks_cache = new_networks
                        
                        # Simpan pilihan sebelumnya
                        sel = listbox.curselection()
                        selected_ssid = listbox.get(sel[0]).split(' (')[0] if sel else None
                        
                        listbox.delete(0, tk.END)
                        
                        new_sel_idx = None
                        for idx, net in enumerate(networks_cache):
                            listbox.insert(tk.END, f"{net['ssid']} (Sinyal: {net['signal']}%)")
                            if selected_ssid and net['ssid'] == selected_ssid:
                                new_sel_idx = idx
                                
                        if new_sel_idx is not None:
                            listbox.selection_set(new_sel_idx)
                            listbox.see(new_sel_idx)
                            
                    status_lbl.config(text="Memindai otomatis setiap 5 detik...")
                    win.after(5000, refresh_networks)
                else:
                    win.after(100, check_result)
                    
            win.after(100, check_result)

        # Mulai loop scanning pertama kali
        refresh_networks()
            
        pass_lbl = tk.Label(win, text="Password Hotspot:", font=("Helvetica", 12), bg="#ecf0f1")
        pass_lbl.pack(pady=(15,0))
        pass_entry = tk.Entry(win, show="*", font=("Helvetica", 14), justify="center")
        pass_entry.pack(pady=5, padx=20, fill=tk.X)
        
        def on_connect():
            sel = listbox.curselection()
            if not sel:
                messagebox.showerror("Error", "Pilih Hotspot WiFi terlebih dahulu dari daftar!", parent=win)
                return
            
            ssid = networks_cache[sel[0]]['ssid']
            password = pass_entry.get()
            
            connect_btn.config(text="Menghubungkan... (Tunggu sebentar)", state=tk.DISABLED)
            win.update()
            
            success, msg = connect_wifi(ssid, password)
            if success:
                self.update_ip_display()
                win.destroy()
                self.show_qr_window()
            else:
                messagebox.showerror("Gagal", f"Gagal terhubung ke {ssid}:\n\n{msg}", parent=win)
                connect_btn.config(text="Hubungkan ke Hotspot", state=tk.NORMAL)
                
        connect_btn = tk.Button(win, text="Hubungkan ke Hotspot", bg="#2980b9", fg="white", font=("Helvetica", 12, "bold"), command=on_connect, cursor="hand2")
        connect_btn.pack(pady=(20, 10), fill=tk.X, padx=20)
        
        def on_skip():
            win.destroy()
            self.show_qr_window()
            
        skip_btn = tk.Button(win, text="Lanjut ke QR Dashboard ➔", bg="#27ae60", fg="white", font=("Helvetica", 12, "bold"), command=on_skip, cursor="hand2")
        skip_btn.pack(pady=(0, 20), fill=tk.X, padx=20)
        
    def show_qr_window_if_connected(self):
        from wifi_manager import get_current_ip
        if get_current_ip() != "127.0.0.1":
            self.show_qr_window()
        else:
            from tkinter import messagebox
            messagebox.showinfo("Belum Terhubung", "Anda harus terhubung ke WiFi/Hotspot terlebih dahulu.\nSilakan klik teks WiFi untuk mengatur koneksi.")
        
    def show_qr_window(self):
        from wifi_manager import get_current_ip
        import qrcode
        from PIL import Image, ImageTk
        
        ip = get_current_ip()
        url = f"http://{ip}:5000"
        
        self.showing_dashboard_qr = True
        
        # Render QR on cam_frame
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((360, 360))
        tk_img = ImageTk.PhotoImage(qr_img)
        
        self.gui.cam_frame.imgtk = tk_img
        self.gui.cam_frame.configure(image=tk_img, bg="white")
        
        # Update text
        self.gui.detected_items_var.set(f"✅ Hotspot Terhubung!\n\nScan QR Code ini dengan HP Anda\nuntuk membuka Dashboard Penjual.\n\nLink: {url}")
        self.gui.items_lbl.configure(bg="#ecf0f1")
        self.gui.btn_detect.configure(state="normal", text="TUTUP DASHBOARD", command=self.close_dashboard_qr)
        
    def close_dashboard_qr(self):
        self.showing_dashboard_qr = False
        self.gui.items_lbl.configure(bg="white")
        self.gui.btn_detect.configure(text="DETEKSI & HITUNG", command=self.gui._handle_detect)
            
    def on_closing(self):
        logger.info("Menutup aplikasi secara aman...")
        self.running = False
        time.sleep(0.5)
        self.camera_manager.release_all()
        if self.btn_fisik:
            self.btn_fisik.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
