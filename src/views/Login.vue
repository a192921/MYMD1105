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

// MSAL 配置 - 修正 redirectUri
const msalConfig = {
  auth: {
    clientId: 'YOUR_CLIENT_ID',
    authority: 'https://login.microsoftonline.com/YOUR_TENANT_ID',
    redirectUri: window.location.origin, // ← 改回根路徑
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  }
};

// Azure AD 登入成功處理 - 增強版
const handleAzureLoginSuccess = async (response) => {
  console.log('Azure AD 登入成功:', response);
  
  // 獲取帳戶資訊
  const account = response.account;
  console.log('使用者資訊:', account);
  
  // 儲存認證資訊
  sessionStorage.setItem('azure_token', response.accessToken);
  sessionStorage.setItem('user_name', account.name);
  sessionStorage.setItem('user_email', account.username);
  sessionStorage.setItem('is_authenticated', 'true'); // ← 新增認證標記
  
  message.success(`歡迎, ${account.name}！`);
  
  // 使用 nextTick 確保資料儲存完成後再跳轉
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // 強制跳轉
  router.push('/dashboard').catch(err => {
    console.error('路由跳轉錯誤:', err);
    // 如果 router.push 失敗,使用 replace
    router.replace('/dashboard');
  });
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

無法成功跳轉至/dashboard