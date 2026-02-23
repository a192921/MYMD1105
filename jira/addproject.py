import tkinter as tk
from tkinter import ttk, messagebox
import requests
from requests.auth import HTTPBasicAuth
import json

'''
幫我用python tkinter 建立一個可以一次建立多個專案的自動化程式
登入 jira 的帳號密碼，後提供使用者填選以下資訊
FIELD_SOURCE_PROJECT: 
FIELD_TARGET_PROJECT:（規則為AWS_project_IPC2/AWS_project_IPC3/AWS_project_IPC4....）
FIELD_TARGET_PROJECT_NAME: （規則為AWS_N12263_CO/AWS_N12264_CO/AWS_N12265_CO....）
FIELD_COPY_COMPONENT: （以勾選的方式，若勾選post "on"，若未勾選不回傳）
生成的專案數量：

建立專案所需的資訊
FIELD_COPY_COMPONENT: "on"
FIELD_SOURCE_PROJECT: "EMPTY_PROJECT"
FIELD_TARGET_PROJECT: "AWS_project_IPC2"
FIELD_TARGET_PROJECT_NAME: "AWS_N12263_CO"
canned-script: "com.onresolve.scriptrunner.canned.jira.admin.CopyProject"
'''
class JiraBatchCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jira ScriptRunner 批次專案建立工具")
        self.root.geometry("600x750")
        
        # API URL
        self.api_url = "http://jira.aws.com.tw/rest/scriptrunner/latest/canned/com.onresolve.scriptrunner.canned.jira.admin.CopyProject"
        
        self.setup_ui()

    def setup_ui(self):
        # 1. 登入資訊
        login_frame = ttk.LabelFrame(self.root, text=" 1. Jira 驗證資訊 ", padding=10)
        login_frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(login_frame, text="帳號 (Username):").grid(row=0, column=0, sticky="w")
        self.ent_user = ttk.Entry(login_frame, width=35)
        self.ent_user.grid(row=0, column=1, pady=2)

        ttk.Label(login_frame, text="密碼 (Password):").grid(row=1, column=0, sticky="w")
        self.ent_pass = ttk.Entry(login_frame, show="*", width=35)
        self.ent_pass.grid(row=1, column=1, pady=2)

        # 2. 專案參數設定
        config_frame = ttk.LabelFrame(self.root, text=" 2. 專案建立規則 (自動遞增) ", padding=10)
        config_frame.pack(fill="x", padx=15, pady=5)

        # Source Project
        ttk.Label(config_frame, text="FIELD_SOURCE_PROJECT:").grid(row=0, column=0, sticky="w")
        self.ent_source = ttk.Entry(config_frame)
        self.ent_source.insert(0, "EMPTY_PROJECT")
        self.ent_source.grid(row=0, column=1, pady=2, sticky="ew")

        # Target Project 起始數字 (AWS_project_IPC2 -> 2)
        ttk.Label(config_frame, text="Target Project 起始數字 (例: 2):").grid(row=1, column=0, sticky="w")
        self.ent_ipc_num = ttk.Entry(config_frame)
        self.ent_ipc_num.insert(0, "2")
        self.ent_ipc_num.grid(row=1, column=1, pady=2, sticky="ew")

        # Target Name 起始數字 (AWS_N12263_CO -> 12263)
        ttk.Label(config_frame, text="Target Name 起始流水號 (例: 12263):").grid(row=2, column=0, sticky="w")
        self.ent_name_num = ttk.Entry(config_frame)
        self.ent_name_num.insert(0, "12263")
        self.ent_name_num.grid(row=2, column=1, pady=2, sticky="ew")

        # Copy Component Checkbox
        self.var_copy_comp = tk.BooleanVar(value=True)
        self.cb_copy_comp = ttk.Checkbutton(config_frame, text="FIELD_COPY_COMPONENT (勾選回傳 'on')", variable=self.var_copy_comp)
        self.cb_copy_comp.grid(row=3, column=0, columnspan=2, pady=5, sticky="w")

        # 生成數量
        ttk.Label(config_frame, text="欲生成的專案總數量:").grid(row=4, column=0, sticky="w")
        self.spin_count = ttk.Spinbox(config_frame, from_=1, to=50, width=10)
        self.spin_count.set(1)
        self.spin_count.grid(row=4, column=1, pady=2, sticky="w")

        # 3. 預覽與日誌
        log_frame = ttk.LabelFrame(self.root, text=" 3. 執行狀態與預覽 ", padding=10)
        log_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.txt_log = tk.Text(log_frame, height=15, font=("Consolas", 9))
        self.txt_log.pack(fill="both", expand=True)

        # 按鈕區
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill="x")

        self.btn_preview = ttk.Button(btn_frame, text="1. 預覽清單", command=self.generate_preview)
        self.btn_preview.pack(side="left", expand=True, fill="x", padx=5)

        self.btn_run = ttk.Button(btn_frame, text="2. 開始批次執行 (POST)", command=self.execute_batch)
        self.btn_run.pack(side="right", expand=True, fill="x", padx=5)

    def get_payload_list(self):
        """根據介面輸入計算出 Payload 清單"""
        try:
            count = int(self.spin_count.get())
            ipc_start = int(self.ent_ipc_num.get())
            name_start = int(self.ent_name_num.get())
            source = self.ent_source.get()
            
            payloads = []
            for i in range(count):
                data = {
                    "FIELD_SOURCE_PROJECT": source,
                    "FIELD_TARGET_PROJECT": f"AWS_project_IPC{ipc_start + i}",
                    "FIELD_TARGET_PROJECT_NAME": f"AWS_N{name_start + i}_CO",
                    "canned-script": "com.onresolve.scriptrunner.canned.jira.admin.CopyProject"
                }
                if self.var_copy_comp.get():
                    data["FIELD_COPY_COMPONENT"] = "on"
                
                payloads.append(data)
            return payloads
        except ValueError:
            messagebox.showerror("錯誤", "起始數字與數量必須為整數")
            return None

    def generate_preview(self):
        payloads = self.get_payload_list()
        if payloads:
            self.txt_log.delete(1.0, tk.END)
            self.txt_log.insert(tk.END, f"--- 預覽即將建立的 {len(payloads)} 個專案 ---\n")
            for p in payloads:
                self.txt_log.insert(tk.END, f"Target: {p['FIELD_TARGET_PROJECT']} | Name: {p['FIELD_TARGET_PROJECT_NAME']}\n")

    def execute_batch(self):
        payloads = self.get_payload_list()
        user = self.ent_user.get()
        password = self.ent_pass.get()

        if not user or not password:
            messagebox.showwarning("警告", "請輸入 Jira 帳號與密碼")
            return

        if not messagebox.askyesno("確認", f"即將發送 {len(payloads)} 個請求至 Jira，確定執行？"):
            return

        self.txt_log.delete(1.0, tk.END)
        self.txt_log.insert(tk.END, "開始執行...\n")

        for i, data in enumerate(payloads):
            try:
                # 設定 Header (ScriptRunner REST 通常需要 X-Atlassian-Token)
                headers = {
                    "Content-Type": "application/json",
                    "X-Atlassian-Token": "no-check"
                }
                
                response = requests.post(
                    self.api_url,
                    json=data,
                    auth=HTTPBasicAuth(user, password),
                    headers=headers,
                    timeout=30
                )

                if response.status_code == 200 or response.status_code == 201:
                    status = "成功"
                else:
                    status = f"失敗 (HTTP {response.status_code})"
                
                self.txt_log.insert(tk.END, f"[{i+1}/{len(payloads)}] {data['FIELD_TARGET_PROJECT']}: {status}\n")
                self.txt_log.see(tk.END)
                self.root.update() # 更新介面顯示

            except Exception as e:
                self.txt_log.insert(tk.END, f"發生錯誤: {str(e)}\n")
        
        messagebox.showinfo("完成", "批次作業執行結束")

if __name__ == "__main__":
    root = tk.Tk()
    app = JiraBatchCreatorApp(root)
    root.mainloop()