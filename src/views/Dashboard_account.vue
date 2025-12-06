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

      <!-- 右上角使用者資訊和登出按鈕 -->
      <div class="floating-actions">
        <!-- 使用者資訊下拉選單 -->
         
        <a-dropdown placement="bottomRight">
          <a-button class="user-info-button" size="large">
            <template #icon>
              <UserOutlined />
            </template>
            <span class="username">Queena</span>
            <DownOutlined style="margin-left: 4px; font-size: 12px" />
          </a-button>
          <template #overlay>
            <a-menu class="user-menu">
              <a-menu-item key="profile" disabled>
                <div class="user-menu-header">
                  <div class="user-menu-name">Queena</div>
                  <div class="user-menu-email">Queena</div>
                </div>
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="profile-settings">
                <UserOutlined style="margin-right: 8px" />
                個人資料
              </a-menu-item>
              <a-menu-item key="settings">
                <SettingOutlined style="margin-right: 8px" />
                系統設定
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout" @click="handleLogout">
                <LogoutOutlined style="margin-right: 8px; color: #ef4444" />
                <span style="color: #ef4444">登出</span>
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>

        <!-- 登出按鈕 (備用，可選擇保留或移除) -->
        <!-- <a-button 
          @click="handleLogout"
          class="floating-logout-button"
          size="large"
        >
          <template #icon>
            <LogoutOutlined />
          </template>
          登出
        </a-button> -->
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
  SettingOutlined
} from '@ant-design/icons-vue';
// import { getUserDisplayName, getUserEmail, logout } from '../utils/auth';
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

// 初始化使用者資訊
// const initUserInfo = () => {
//   // 優先從 auth.js 取得 MSAL 使用者資訊
//   const msalUsername = getUserDisplayName();
//   const msalEmail = getUserEmail();
  
//   if (msalUsername) {
//     username.value = msalUsername;
//     userEmail.value = msalEmail;
//   } else {
//     // 如果 MSAL 沒有資料，從 localStorage 取得
//     username.value = localStorage.getItem('username') || '使用者';
//     userEmail.value = localStorage.getItem('userEmail') || '';
//   }
// };

// 登出處理
const handleLogout = async () => {
  try {
    // 使用 MSAL 登出
    await logout();
    message.success('登出成功！');
  } catch (error) {
    console.error('登出失敗:', error);
    // 即使 MSAL 登出失敗，也清除本地資料
    localStorage.removeItem('username');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('token');
    message.success('登出成功！');
    router.push('/login');
  }
};

// 組件掛載時初始化使用者資訊
onMounted(() => {
  initUserInfo();
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

/* 右上角浮動操作區 */
.floating-actions {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 1000;
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 使用者資訊按鈕 */
.user-info-button {
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

.user-info-button:hover {
  background: #f9fafb !important;
  border-color: #d1d5db !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.user-info-button .username {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #1f2937;
}

.user-info-button .anticon-user {
  font-size: 16px;
  color: #667eea;
}

.user-info-button .anticon-down {
  color: #9ca3af;
}

/* 使用者下拉選單 */
.user-menu {
  min-width: 220px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 8px;
}

.user-menu-header {
  padding: 8px 4px;
}

.user-menu-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.user-menu-email {
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

/* 浮動登出按鈕 (如果保留) */
.floating-logout-button {
  height: 44px;
  padding: 0 20px;
  font-size: 15px;
  font-weight: 500;
  background: #b4b7bb;
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.floating-logout-button:hover {
  background: #4b5563 !important;
  color: white !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(107, 114, 128, 0.4);
}

.floating-logout-button:active {
  transform: translateY(0);
  background: #374151 !important;
}

.content {
  background: #f5f5f5;
  min-height: 100vh;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .floating-actions {
    top: 16px;
    right: 16px;
  }

  .user-info-button .username {
    max-width: 80px;
  }
}
</style>