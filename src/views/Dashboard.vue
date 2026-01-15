<template>
  <a-layout class="layout">
    <a-layout-sider width="280" class="sidebar">
      <div class="logo-section">
        <div class="logo-text">
          <div class="logo-title">MYMD</div>
          <div class="logo-subtitle">Admin</div>
        </div>
      </div>
      
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        class="menu"
        @click="handleMenuClick"
      >
        <a-menu-item key="overview">
          <template #icon><BarChartOutlined /></template>
          系統總覽
        </a-menu-item>
        <a-menu-item key="users">
          <template #icon><TeamOutlined /></template>
          使用者管理
        </a-menu-item>
        <a-menu-item key="features">
          <template #icon><AppstoreOutlined /></template>
          功能管理
        </a-menu-item>
        <a-menu-item key="jobs">
          <template #icon><MonitorOutlined /></template>
          Job監控
        </a-menu-item>
        <a-menu-item key="audit">
          <template #icon><FileTextOutlined /></template>
          Audit log
        </a-menu-item>
      </a-menu>
    </a-layout-sider>

    <a-layout>
      <!-- 主要內容區 -->
      <a-layout-content class="content">
        <component :is="currentComponent" />
      </a-layout-content>

      <!-- 右上角使用者帳戶按鈕 -->
      <div class="floating-user-button">
        <a-dropdown placement="bottomRight" :trigger="['click']">
          <a-button class="user-button" size="large" :loading="loadingUserInfo">
            <UserOutlined v-if="!loadingUserInfo" />
            <span class="username">{{ username || '載入中...' }}</span>
            <DownOutlined style="margin-left: 4px; font-size: 12px" />
          </a-button>
          <template #overlay>
            <a-menu class="user-menu" @click="handleUserMenuClick">
              <a-menu-item key="profile" disabled>
                <div class="user-info">
                  <div class="user-name">{{ username || '使用者' }}</div>
                  <div class="user-email">{{ userEmail || '載入中...' }}</div>
                </div>
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout">
                <LogoutOutlined style="margin-right: 8px; color: #ef4444" />
                <span style="color: #ef4444">登出</span>
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, markRaw, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  BarChartOutlined,
  TeamOutlined,
  AppstoreOutlined,
  MonitorOutlined,
  FileTextOutlined,
  LogoutOutlined,
  UserOutlined,
  DownOutlined,
} from '@ant-design/icons-vue';
import { api } from '../utils/api';
import Overview from '../components/Overview.vue';
import UserManagement from '../components/UserManagement.vue';
import FeatureManagement from '../components/FeatureManagement.vue';
import JobManagement from '../components/JobManagement.vue';
import Audit from '../components/Audit.vue';

const router = useRouter();
const selectedKeys = ref(['overview']);

// 使用者資訊
const username = ref('');
const userEmail = ref('');
const loadingUserInfo = ref(false);

const components = {
  overview: markRaw(Overview),
  users: markRaw(UserManagement),
  features: markRaw(FeatureManagement),
  jobs: markRaw(JobManagement),
  audit: markRaw(Audit)
};

const currentComponent = computed(() => components[selectedKeys.value[0]]);

const handleMenuClick = ({ key }) => {
  selectedKeys.value = [key];
};

// 取得使用者資訊
const fetchUserInfo = async () => {
  loadingUserInfo.value = true;
  
  try {
    // API: GET /api/user/profile 或 /api/user/me
    const response = await api.get('/api/user/profile');
    
    console.log('使用者資訊 API 回應:', response.data);
    
    // 處理不同的 API 回應格式
    let userData = null;
    
    if (response.data && response.data.res && response.data.res.data) {
      userData = response.data.res.data;
    } else if (response.data && response.data.data) {
      userData = response.data.data;
    } else if (response.data) {
      userData = response.data;
    }
    
    if (userData) {
      // 根據實際 API 欄位名稱調整
      username.value = userData.displayName || userData.username || userData.name || '使用者';
      userEmail.value = userData.email || userData.mail || '';
      
      // 儲存到 localStorage（選用）
      localStorage.setItem('username', username.value);
      localStorage.setItem('userEmail', userEmail.value);
      
      console.log('使用者資訊:', { username: username.value, userEmail: userEmail.value });
    } else {
      throw new Error('無法解析使用者資訊');
    }
    
  } catch (error) {
    console.error('取得使用者資訊失敗:', error);
    
    // 嘗試從 localStorage 讀取
    const cachedUsername = localStorage.getItem('username');
    const cachedEmail = localStorage.getItem('userEmail');
    
    if (cachedUsername) {
      username.value = cachedUsername;
      userEmail.value = cachedEmail || '';
      console.log('使用快取的使用者資訊');
    } else {
      // 使用假資料作為後備
      username.value = '王小明';
      userEmail.value = 'wang.xiaoming@company.com';
      message.warning('無法取得使用者資訊，使用預設資料');
    }
  } finally {
    loadingUserInfo.value = false;
  }
};

// 處理使用者選單點擊
const handleUserMenuClick = ({ key }) => {
  switch (key) {
    case 'logout':
      handleLogout();
      break;
  }
};

const handleLogout = () => {
  message.success('登出成功！');
  
  // 清除登入狀態
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  localStorage.removeItem('userEmail');
  
  // 導向登入頁
  router.push('/login');
};

// 頁面載入時取得使用者資訊
onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.sidebar {
  background: #334155;
  padding: 24px 16px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
  padding: 0 8px;
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.logo-title {
  font-size: 32px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 1px;
  line-height: 1;
}

.logo-subtitle {
  font-size: 16px;
  font-weight: 500;
  color: #94a3b8;
  letter-spacing: 0.5px;
}

.menu {
  background: transparent;
  border: none;
}

:deep(.ant-menu-dark .ant-menu-item-selected) {
  background: #facc15 !important;
  color: #1e293b !important;
  font-weight: 600;
}

:deep(.ant-menu-dark .ant-menu-item-selected .anticon) {
  color: #1e293b !important;
}

:deep(.ant-menu-dark .ant-menu-item) {
  color: white;
  font-size: 15px;
  height: 44px;
  line-height: 44px;
  margin: 4px 0;
  border-radius: 8px;
}

:deep(.ant-menu-dark .ant-menu-item:hover) {
  background: #475569;
}

.content {
  background: #f5f5f5;
  min-height: 100vh;
}

/* 右上角使用者按鈕 */
.floating-user-button {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 1000;
}

.user-button {
  height: 44px;
  padding: 0 16px;
  font-size: 15px;
  font-weight: 500;
  background: white;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-button:hover {
  background: #f9fafb !important;
  border-color: #d1d5db !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.user-button .anticon-user {
  font-size: 16px;
  color: #667eea;
}

.username {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #1f2937;
}

.user-button .anticon-down {
  color: #9ca3af;
}

/* 使用者下拉選單 */
.user-menu {
  min-width: 220px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 8px;
}

.user-info {
  padding: 8px 4px;
}

.user-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.user-email {
  font-size: 13px;
  color: #6b7280;
  word-break: break-all;
}

.user-menu :deep(.ant-dropdown-menu-item) {
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 14px;
}

.user-menu :deep(.ant-dropdown-menu-item:hover) {
  background: #f3f4f6;
}

.user-menu :deep(.ant-dropdown-menu-item-disabled) {
  cursor: default;
}

.user-menu :deep(.ant-dropdown-menu-item-disabled:hover) {
  background: transparent;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .floating-user-button {
    top: 16px;
    right: 16px;
  }

  .username {
    max-width: 80px;
  }
}
</style>