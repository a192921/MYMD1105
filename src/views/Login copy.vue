<!-- Login.vue -->
<template>
  <div class="login-container">
    <a-card class="login-card" :bordered="false">
      <div class="logo-section">
        <div class="logo-icon">
          <ToolOutlined style="font-size: 32px; color: white" />
        </div>
        <div class="logo-text">
          <div class="logo-title">MYMD</div>
          <div class="logo-subtitle">Admin System</div>
        </div>
      </div>

      <div class="login-description">
        <p>請使用您的 Microsoft 帳戶登入</p>
      </div>

      <!-- Azure AD 登入按鈕 -->
      <a-button 
        class="azure-login-button"
        size="large"
        block
        @click="handleAzureLogin"
        :loading="azureLoading"
      >
        <template #icon>
          <WindowsOutlined />
        </template>
        使用 Microsoft 帳戶登入
      </a-button>

      <div class="login-footer">
        <a-alert 
          v-if="errorMessage"
          :message="errorMessage" 
          type="error" 
          closable
          @close="errorMessage = ''"
          style="margin-top: 16px"
        />
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
  ToolOutlined,
  WindowsOutlined 
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { PublicClientApplication } from '@azure/msal-browser';

const router = useRouter();
const azureLoading = ref(false);
const errorMessage = ref('');

// MSAL 配置
const msalConfig = {
  auth: {
    clientId: 'YOUR_CLIENT_ID', // 替換為你的 Azure AD Client ID
    authority: 'https://login.microsoftonline.com/YOUR_TENANT_ID', // 替換為你的 Tenant ID
    redirectUri: window.location.origin + '/dashboard', // 登入成功後跳轉的 URL
  },
  cache: {
    cacheLocation: 'sessionStorage', // 可選 'localStorage' 或 'sessionStorage'
    storeAuthStateInCookie: false,
  }
};

// 登入請求配置
const loginRequest = {
  scopes: ['User.Read'] // 請求的權限範圍
};

// 初始化 MSAL 實例
let msalInstance = null;

onMounted(async () => {
  try {
    msalInstance = new PublicClientApplication(msalConfig);
    await msalInstance.initialize();
    
    // 處理重定向回來的回應
    const response = await msalInstance.handleRedirectPromise();
    if (response) {
      handleAzureLoginSuccess(response);
    }
  } catch (error) {
    console.error('MSAL 初始化錯誤:', error);
    errorMessage.value = 'Azure AD 服務初始化失敗，請重新整理頁面';
  }
});

// Azure AD 登入
const handleAzureLogin = async () => {
  if (!msalInstance) {
    message.error('MSAL 尚未初始化，請稍後再試');
    return;
  }

  azureLoading.value = true;
  errorMessage.value = '';

  try {
    // 使用彈出視窗登入
    const response = await msalInstance.loginPopup(loginRequest);
    handleAzureLoginSuccess(response);
  } catch (error) {
    console.error('Azure AD 登入錯誤:', error);
    
    if (error.errorCode === 'user_cancelled') {
      message.warning('登入已取消');
    } else if (error.errorCode === 'popup_window_error') {
      errorMessage.value = '無法開啟登入視窗，請檢查瀏覽器彈出視窗設定';
    } else {
      errorMessage.value = 'Azure AD 登入失敗: ' + error.message;
      message.error('登入失敗，請稍後再試');
    }
  } finally {
    azureLoading.value = false;
  }
};

// Azure AD 登入成功處理
const handleAzureLoginSuccess = (response) => {
  console.log('Azure AD 登入成功:', response);
  
  // 獲取帳戶資訊
  const account = response.account;
  console.log('使用者資訊:', account);
  
  // 儲存 token（實際應用中應該傳送到後端驗證）
  sessionStorage.setItem('azure_token', response.accessToken);
  sessionStorage.setItem('user_name', account.name);
  sessionStorage.setItem('user_email', account.username);
  
  message.success(`歡迎, ${account.name}！`);
  router.push('/dashboard');
};

// 取得 Access Token（用於 API 呼叫）
const getAccessToken = async () => {
  if (!msalInstance) return null;

  const accounts = msalInstance.getAllAccounts();
  if (accounts.length === 0) return null;

  try {
    const response = await msalInstance.acquireTokenSilent({
      ...loginRequest,
      account: accounts[0]
    });
    return response.accessToken;
  } catch (error) {
    console.error('取得 Token 錯誤:', error);
    return null;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #4f4ba2 100%);
}

.login-card {
  width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 20px;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.logo-text {
  text-align: center;
}

.logo-title {
  font-size: 36px;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: 2px;
}

.logo-subtitle {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.login-description {
  text-align: center;
  margin-bottom: 24px;
}

.login-description p {
  color: #64748b;
  font-size: 15px;
  margin: 0;
}

.azure-login-button {
  background: #0078d4;
  color: white;
  border: none;
  font-weight: 500;
  height: 48px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.azure-login-button:hover {
  background: #106ebe !important;
  color: white !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 120, 212, 0.4);
}

.azure-login-button:active {
  transform: translateY(0);
}

.login-footer {
  margin-top: 16px;
}
</style>


<!-- ============================================ -->
<!-- package.json 需要安裝的套件 -->
<!-- ============================================ -->
{
  "dependencies": {
    "@azure/msal-browser": "^3.7.0"
  }
}

<!-- 安裝指令 -->
<!-- npm install @azure/msal-browser -->


<!-- ============================================ -->
<!-- Azure AD 設定步驟 -->
<!-- ============================================ -->

1. 前往 Azure Portal (https://portal.azure.com)
2. 進入「Azure Active Directory」
3. 選擇「App registrations」→「New registration」
4. 設定應用程式：
   - Name: MYMD Admin
   - Supported account types: 選擇適合的類型
   - Redirect URI: 
     * Platform: Single-page application (SPA)
     * URI: http://localhost:5173/dashboard (開發環境)
            https://yourdomain.com/dashboard (正式環境)

5. 註冊後，複製以下資訊：
   - Application (client) ID → 替換 YOUR_CLIENT_ID
   - Directory (tenant) ID → 替換 YOUR_TENANT_ID

6. 設定 API 權限：
   - 點選「API permissions」
   - 「Add a permission」→「Microsoft Graph」
   - 選擇「Delegated permissions」
   - 勾選「User.Read」
   - 點選「Grant admin consent」

7. 設定驗證：
   - 點選「Authentication」
   - 確認 Redirect URIs 正確
   - 勾選「Access tokens」和「ID tokens」

 

<!-- ============================================ -->
<!-- 程式碼中需要修改的地方 -->
<!-- ============================================ -->

const msalConfig = {
  auth: {
    clientId: 'YOUR_CLIENT_ID',  // ← 替換這裡
    authority: 'https://login.microsoftonline.com/YOUR_TENANT_ID',  // ← 替換這裡
    redirectUri: window.location.origin + '/dashboard',
  },
  // ...
};

