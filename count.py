import tkinter as tk
from tkinter import messagebox
import pygame  # 用於播放 MP3
import os

class mp3Timer:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 自定義計時器")
        self.root.geometry("350x550")
        
        # 初始化 pygame 混音器
        pygame.mixer.init()
        
        # 請確保你的 MP3 檔案放在程式碼同一個資料夾，檔名改為 "bell.mp3"
        # 或者你可以修改下方的檔名
        self.sound_file = "bell.mp3" 
        
        self.remaining_seconds = 0
        self.is_running = False
        self.alert_minutes = set()
        self.after_id = None

        # --- 介面設計 ---
        tk.Label(root, text="1. 設定總倒數分鐘:", font=("Arial", 10, "bold")).pack(pady=(15, 0))
        self.entry_total = tk.Entry(root, font=("Arial", 12), width=10, justify='center')
        self.entry_total.insert(0, "60")
        self.entry_total.pack(pady=5)

        tk.Label(root, text="2. 新增響鈴點 (分鐘):", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        frame_input = tk.Frame(root)
        frame_input.pack()
        self.entry_alert = tk.Entry(frame_input, font=("Arial", 12), width=8)
        self.entry_alert.pack(side="left", padx=5)
        btn_add = tk.Button(frame_input, text="新增", command=self.add_alert)
        btn_add.pack(side="left")

        self.listbox = tk.Listbox(root, height=5, width=30)
        self.listbox.pack(pady=10)
        
        btn_del = tk.Button(root, text="刪除選中的響鈴點", command=self.del_alert, fg="red")
        btn_del.pack()

        # 檢查 MP3 檔案是否存在
        self.status_label = tk.Label(root, text="", fg="blue", font=("Arial", 9))
        self.status_label.pack()
        self.check_file()

        self.label_display = tk.Label(root, text="00:00", font=("Helvetica", 48), fg="#2C3E50")
        self.label_display.pack(pady=20)

        # 核心控制按鈕 (開始 / 停止)
        self.btn_control = tk.Button(root, text="開始倒數", font=("Arial", 14, "bold"), 
                                     bg="#27ae60", fg="white", width=20, height=2,
                                     command=self.toggle_timer)
        self.btn_control.pack(pady=10)

    def check_file(self):
        if os.path.exists(self.sound_file):
            self.status_label.config(text=f"已偵測到音效檔: {self.sound_file}", fg="green")
        else:
            self.status_label.config(text="警告: 找不到 bell.mp3，將使用預設嗶聲", fg="red")

    def play_sound(self):
        """播放 MP3，若失敗則播放系統嗶聲"""
        if os.path.exists(self.sound_file):
            try:
                pygame.mixer.music.load(self.sound_file)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"播放失敗: {e}")
        else:
            # 如果找不到 MP3，就用 Windows 嗶聲替代
            import winsound
            winsound.Beep(1000, 600)

    def add_alert(self):
        val = self.entry_alert.get()
        if val.isdigit():
            m = int(val)
            if m not in self.alert_minutes:
                self.alert_minutes.add(m)
                self.listbox.insert(tk.END, f"剩餘 {m} 分鐘時響鈴")
                self.entry_alert.delete(0, tk.END)

    def del_alert(self):
        selection = self.listbox.curselection()
        if selection:
            text = self.listbox.get(selection)
            m = int(text.split()[1])
            self.alert_minutes.remove(m)
            self.listbox.delete(selection)

    def toggle_timer(self):
        if not self.is_running:
            self.start_countdown()
        else:
            self.stop_countdown()

    def start_countdown(self):
        try:
            total_m = int(self.entry_total.get())
            if total_m <= 0: raise ValueError
            self.remaining_seconds = total_m * 60
            self.is_running = True
            self.btn_control.config(text="停止倒數", bg="#e74c3c")
            self.update_clock()
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的總分鐘數")

    def stop_countdown(self):
        self.is_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.btn_control.config(text="開始倒數", bg="#27ae60")
        self.label_display.config(text="00:00")

    def update_clock(self):
        if self.is_running and self.remaining_seconds >= 0:
            mins, secs = divmod(self.remaining_seconds, 60)
            self.label_display.config(text=f"{mins:02d}:{secs:02d}")

            # 檢查響鈴時間點
            if secs == 0 and mins in self.alert_minutes and self.remaining_seconds != 0:
                self.play_sound()

            if self.remaining_seconds > 0:
                self.remaining_seconds -= 1
                self.after_id = self.root.after(1000, self.update_clock)
            else:
                self.is_running = False
                self.play_sound()
                self.btn_control.config(text="開始倒數", bg="#27ae60")
                messagebox.showinfo("完成", "計時結束！")

if __name__ == "__main__":
    root = tk.Tk()
    app = mp3Timer(root)
    root.mainloop()