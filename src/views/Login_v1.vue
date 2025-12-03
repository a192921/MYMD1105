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
import { ToolOutlined, WindowsOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { 
  initializeMsal, 
  loginWithRedirect,
  getUserDisplayName 
} from '@/utils/auth';

// ============================================
// Router
// ============================================
const router = useRouter();

// ============================================
// 狀態管理
// ============================================
const isLoggingIn = ref(false);
const errorMessage = ref('');

// ============================================
// 初始化 MSAL（處理重定向回應）
// ============================================
const initAuth = async () => {
  try {
    const result = await initializeMsal();

    if (result.success) {
      if (result.alreadyLoggedIn) {
        // 使用者已經登入
        const displayName = getUserDisplayName();
        message.success(`歡迎回來，${displayName}`);
        
        // 跳轉到儀表板
        router.push('/dashboard');
      } else {
        // 剛完成登入（從重定向回來）
        const displayName = result.account.name || result.account.username;
        message.success(`登入成功！歡迎 ${displayName}`);
        
        // 跳轉到儀表板
        setTimeout(() => {
          router.push('/dashboard');
        }, 500);
      }
    }
  } catch (error) {
    console.error('初始化認證失敗:', error);
    errorMessage.value = error.message || 'Azure AD 服務初始化失敗';
  }
};

// ============================================
// 處理登入按鈕點擊
// ============================================
const handleLogin = async () => {
  isLoggingIn.value = true;
  errorMessage.value = '';

  try {
    // 使用重定向方式登入
    await loginWithRedirect();
    
    // 注意：loginWithRedirect 會導致頁面重定向
    // 所以這裡的程式碼不會執行
  } catch (error) {
    console.error('登入失敗:', error);
    errorMessage.value = error.message || '登入失敗，請稍後再試';
    isLoggingIn.value = false;
  }
};

// ============================================
// 組件生命週期
// ============================================
onMounted(async () => {
  // 初始化 MSAL 並處理重定向回應
  await initAuth();
});
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

