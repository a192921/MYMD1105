"""
Azure Entra ID Access Token 取得器 - GUI 版本
使用 Tkinter 和 MSAL 來建立簡單的登入介面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from msal import PublicClientApplication
import threading
import pyperclip

class AzureTokenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure Entra ID Token 取得器")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # 設定樣式
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 標題
        title_label = ttk.Label(
            main_frame, 
            text="Azure Entra ID Access Token 取得器",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Azure 設定區域
        config_frame = ttk.LabelFrame(main_frame, text="Azure 設定", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Client ID
        ttk.Label(config_frame, text="Client ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.client_id_var = tk.StringVar()
        client_id_entry = ttk.Entry(config_frame, textvariable=self.client_id_var, width=50)
        client_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Tenant ID
        ttk.Label(config_frame, text="Tenant ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tenant_id_var = tk.StringVar()
        tenant_id_entry = ttk.Entry(config_frame, textvariable=self.tenant_id_var, width=50)
        tenant_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Scopes
        ttk.Label(config_frame, text="Scopes:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.scopes_var = tk.StringVar(value="User.Read")
        scopes_entry = ttk.Entry(config_frame, textvariable=self.scopes_var, width=50)
        scopes_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(
            config_frame, 
            text="(多個 scope 請用空格分隔)", 
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # 登入資訊區域
        login_frame = ttk.LabelFrame(main_frame, text="登入資訊", padding="10")
        login_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Username
        ttk.Label(login_frame, text="帳號 (Email):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(login_frame, textvariable=self.username_var, width=50)
        username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(login_frame, text="密碼:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(login_frame, textvariable=self.password_var, width=50, show="●")
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 綁定 Enter 鍵
        password_entry.bind('<Return>', lambda e: self.get_token())
        
        # 按鈕區域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.login_button = ttk.Button(
            button_frame,
            text="取得 Access Token",
            command=self.get_token,
            width=20
        )
        self.login_button.grid(row=0, column=0, padx=5)
        
        self.clear_button = ttk.Button(
            button_frame,
            text="清除",
            command=self.clear_all,
            width=15
        )
        self.clear_button.grid(row=0, column=1, padx=5)
        
        # 結果顯示區域
        result_frame = ttk.LabelFrame(main_frame, text="結果", padding="10")
        result_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 狀態標籤
        self.status_label = ttk.Label(result_frame, text="尚未登入", foreground="gray")
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Token 顯示區域
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            height=15,
            width=75,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 複製按鈕
        self.copy_button = ttk.Button(
            result_frame,
            text="複製 Access Token",
            command=self.copy_token,
            state=tk.DISABLED
        )
        self.copy_button.grid(row=2, column=0, pady=(10, 0))
        
        # 進度條
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=660
        )
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 儲存 token
        self.current_token = None
        
    def get_token(self):
        """取得 Access Token"""
        # 驗證輸入
        if not self.client_id_var.get():
            messagebox.showerror("錯誤", "請輸入 Client ID")
            return
        if not self.tenant_id_var.get():
            messagebox.showerror("錯誤", "請輸入 Tenant ID")
            return
        if not self.username_var.get():
            messagebox.showerror("錯誤", "請輸入帳號")
            return
        if not self.password_var.get():
            messagebox.showerror("錯誤", "請輸入密碼")
            return
        
        # 在背景執行緒中執行登入
        thread = threading.Thread(target=self._get_token_thread, daemon=True)
        thread.start()
    
    def _get_token_thread(self):
        """在背景執行緒中取得 token"""
        # 更新 UI
        self.root.after(0, self._update_ui_start)
        
        try:
            # 建立 MSAL 應用程式
            authority = f"https://login.microsoftonline.com/{self.tenant_id_var.get()}"
            app = PublicClientApplication(
                client_id=self.client_id_var.get(),
                authority=authority
            )
            
            # 解析 scopes
            scopes = self.scopes_var.get().split()
            
            # 取得 token
            result = app.acquire_token_by_username_password(
                username=self.username_var.get(),
                password=self.password_var.get(),
                scopes=scopes
            )
            
            # 更新 UI
            self.root.after(0, lambda: self._update_ui_complete(result))
            
        except Exception as e:
            self.root.after(0, lambda: self._update_ui_error(str(e)))
    
    def _update_ui_start(self):
        """開始取得 token 時更新 UI"""
        self.login_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在登入...", foreground="blue")
        self.result_text.delete(1.0, tk.END)
        self.progress.start(10)
        self.current_token = None
    
    def _update_ui_complete(self, result):
        """取得 token 完成時更新 UI"""
        self.progress.stop()
        self.login_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        
        if "access_token" in result:
            # 成功取得 token
            self.current_token = result["access_token"]
            self.status_label.config(text="✅ 成功取得 Access Token", foreground="green")
            self.copy_button.config(state=tk.NORMAL)
            
            # 顯示結果
            output = "=" * 70 + "\n"
            output += "Access Token (完整)\n"
            output += "=" * 70 + "\n"
            output += f"{self.current_token}\n\n"
            
            output += "=" * 70 + "\n"
            output += "Token 資訊\n"
            output += "=" * 70 + "\n"
            output += f"Token 類型: {result.get('token_type', 'N/A')}\n"
            output += f"過期時間: {result.get('expires_in', 'N/A')} 秒\n"
            
            if "id_token_claims" in result:
                claims = result["id_token_claims"]
                output += f"\n使用者資訊:\n"
                output += f"  名稱: {claims.get('name', 'N/A')}\n"
                output += f"  Email: {claims.get('preferred_username', 'N/A')}\n"
                output += f"  租戶 ID: {claims.get('tid', 'N/A')}\n"
            
            output += "\n" + "=" * 70 + "\n"
            output += "使用方式 (Python 範例)\n"
            output += "=" * 70 + "\n"
            output += "import requests\n\n"
            output += "headers = {\n"
            output += f"    'Authorization': 'Bearer {self.current_token[:30]}...'\n"
            output += "}\n\n"
            output += "response = requests.get(\n"
            output += "    'https://graph.microsoft.com/v1.0/me',\n"
            output += "    headers=headers\n"
            output += ")\n"
            
            self.result_text.insert(1.0, output)
            
        else:
            # 取得 token 失敗
            self.status_label.config(text="❌ 取得 Token 失敗", foreground="red")
            
            output = "=" * 70 + "\n"
            output += "錯誤資訊\n"
            output += "=" * 70 + "\n"
            output += f"錯誤代碼: {result.get('error', 'N/A')}\n\n"
            output += f"錯誤描述:\n{result.get('error_description', 'N/A')}\n\n"
            
            # 常見錯誤提示
            error_code = result.get('error', '')
            if 'invalid_grant' in error_code:
                output += "\n💡 提示:\n"
                output += "- 請確認帳號和密碼是否正確\n"
                output += "- 如果帳戶啟用了 MFA (多因素驗證)，無法使用密碼登入\n"
                output += "- 請確認帳戶未被鎖定或停用\n"
            elif 'invalid_client' in error_code:
                output += "\n💡 提示:\n"
                output += "- 請確認 Client ID 是否正確\n"
                output += "- 請確認應用程式註冊設定是否正確\n"
            elif 'unauthorized_client' in error_code:
                output += "\n💡 提示:\n"
                output += "- 請在 Azure Portal 的應用程式註冊中啟用「允許公用用戶端流程」\n"
                output += "- 路徑: 驗證 > 進階設定 > 允許公用用戶端流程 > 是\n"
            
            self.result_text.insert(1.0, output)
    
    def _update_ui_error(self, error_message):
        """發生錯誤時更新 UI"""
        self.progress.stop()
        self.login_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        self.status_label.config(text="❌ 發生錯誤", foreground="red")
        
        output = "=" * 70 + "\n"
        output += "系統錯誤\n"
        output += "=" * 70 + "\n"
        output += f"{error_message}\n"
        
        self.result_text.insert(1.0, output)
    
    def copy_token(self):
        """複製 token 到剪貼簿"""
        if self.current_token:
            try:
                pyperclip.copy(self.current_token)
                messagebox.showinfo("成功", "Access Token 已複製到剪貼簿!")
            except Exception as e:
                # 如果 pyperclip 無法使用，使用替代方案
                self.root.clipboard_clear()
                self.root.clipboard_append(self.current_token)
                self.root.update()
                messagebox.showinfo("成功", "Access Token 已複製到剪貼簿!")
    
    def clear_all(self):
        """清除所有內容"""
        self.result_text.delete(1.0, tk.END)
        self.password_var.set("")
        self.status_label.config(text="尚未登入", foreground="gray")
        self.copy_button.config(state=tk.DISABLED)
        self.current_token = None


def main():
    """主程式"""
    # 檢查必要套件
    try:
        import msal
    except ImportError:
        import sys
        print("錯誤: 請先安裝 msal 套件")
        print("執行: pip install msal")
        sys.exit(1)
    
    try:
        import pyperclip
    except ImportError:
        print("警告: pyperclip 套件未安裝，複製功能可能受限")
        print("建議執行: pip install pyperclip")
    
    # 建立主視窗
    root = tk.Tk()
    app = AzureTokenApp(root)
    
    # 執行主迴圈
    root.mainloop()


if __name__ == "__main__":
    main()