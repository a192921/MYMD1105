"""
Azure Entra ID Access Token 取得範例
使用 MSAL (Microsoft Authentication Library) 來取得 access token
"""

from msal import PublicClientApplication
import sys

# 配置參數 - 請替換成你的實際值
CLIENT_ID = "YOUR_CLIENT_ID_HERE"  # 應用程式(用戶端)識別碼
TENANT_ID = "YOUR_TENANT_ID_HERE"  # 目錄(租戶)識別碼
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# 定義需要的權限範圍
# 選項 1: 針對 Microsoft Graph
SCOPES = ["User.Read"]

# 選項 2: 針對你自己的 API (如果已設定 "公開 API")
# SCOPES = [f"api://{CLIENT_ID}/access_as_user"]


def get_access_token_interactive():
    """
    使用互動式瀏覽器登入方式取得 access token
    適合桌面應用程式或需要使用者互動的場景
    """
    # 建立公開用戶端應用程式
    app = PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY
    )
    
    # 首先嘗試從快取中取得 token
    accounts = app.get_accounts()
    result = None
    
    if accounts:
        print("找到快取的帳戶,嘗試靜默取得 token...")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    
    # 如果快取中沒有 token,使用互動式登入
    if not result:
        print("需要互動式登入...")
        result = app.acquire_token_interactive(
            scopes=SCOPES,
            # 可選參數
            # prompt="select_account",  # 強制選擇帳戶
        )
    
    return result


def get_access_token_device_code():
    """
    使用裝置代碼流程取得 access token
    適合無法開啟瀏覽器的環境(如遠端伺服器、容器等)
    """
    app = PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY
    )
    
    # 啟動裝置代碼流程
    flow = app.initiate_device_flow(scopes=SCOPES)
    
    if "user_code" not in flow:
        raise ValueError(f"無法啟動裝置代碼流程: {flow.get('error_description')}")
    
    # 顯示使用者需要執行的操作
    print(flow["message"])
    
    # 等待使用者完成驗證
    result = app.acquire_token_by_device_flow(flow)
    
    return result


def get_access_token_username_password(username, password):
    """
    使用用戶名和密碼取得 access token
    注意: 此方法不支援 MFA,不建議用於生產環境
    """
    app = PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY
    )
    
    result = app.acquire_token_by_username_password(
        username=username,
        password=password,
        scopes=SCOPES
    )
    
    return result


def display_token_info(result):
    """顯示 token 資訊"""
    if "access_token" in result:
        print("\n✅ 成功取得 Access Token!")
        print(f"\nAccess Token (前50字元): {result['access_token'][:50]}...")
        print(f"Token 類型: {result.get('token_type', 'N/A')}")
        print(f"過期時間: {result.get('expires_in', 'N/A')} 秒")
        
        if "id_token_claims" in result:
            claims = result["id_token_claims"]
            print(f"\n使用者資訊:")
            print(f"  名稱: {claims.get('name', 'N/A')}")
            print(f"  Email: {claims.get('preferred_username', 'N/A')}")
        
        return result["access_token"]
    else:
        print("\n❌ 取得 token 失敗!")
        print(f"錯誤: {result.get('error', 'N/A')}")
        print(f"錯誤描述: {result.get('error_description', 'N/A')}")
        return None


def main():
    """主程式"""
    print("=" * 60)
    print("Azure Entra ID Access Token 取得範例")
    print("=" * 60)
    
    print("\n請選擇驗證方式:")
    print("1. 互動式瀏覽器登入 (推薦)")
    print("2. 裝置代碼流程 (適合遠端環境)")
    print("3. 用戶名/密碼 (不建議)")
    
    choice = input("\n請輸入選項 (1-3): ").strip()
    
    try:
        if choice == "1":
            result = get_access_token_interactive()
        elif choice == "2":
            result = get_access_token_device_code()
        elif choice == "3":
            username = input("請輸入用戶名 (email): ")
            password = input("請輸入密碼: ")
            result = get_access_token_username_password(username, password)
        else:
            print("無效的選項!")
            return
        
        # 顯示結果
        access_token = display_token_info(result)
        
        # 可以將 token 用於後續的 API 呼叫
        if access_token:
            print("\n你現在可以使用此 token 來呼叫 API:")
            print(f'headers = {{"Authorization": "Bearer {access_token[:30]}..."}}')
            
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 檢查是否已安裝 msal
    try:
        import msal
    except ImportError:
        print("請先安裝 msal 套件:")
        print("pip install msal")
        sys.exit(1)
    
    main()