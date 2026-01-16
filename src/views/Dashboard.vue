<template>
  <a-layout class="layout">
    <a-layout-sider width="280" class="sidebar">
      <div class="logo-section">
        <div class="logo-text">
          <div class="logo-title">MYMD</div>
          <div class="logo-subtitle">Admin</div>
        </div>
      </div>

      <!-- 使用者資訊卡片 -->
      <div class="user-info-card" v-if="!loadingUserInfo">
        <div class="user-avatar">
          <UserOutlined />
        </div>
        <div class="user-details">
          <div class="user-name">{{ username || '使用者' }}</div>
          <div class="user-meta">
            <div class="user-account-id">{{ accountId || '-' }}</div>
            <div class="user-role-badge" :class="getRoleClass(role)">
              {{ getRoleLabel(role) }}
            </div>
          </div>
          <div class="user-email">{{ userEmail || '-' }}</div>
        </div>
      </div>

      <!-- 載入中狀態 -->
      <div class="user-info-card loading" v-else>
        <a-spin />
        <span style="margin-left: 12px; color: #94a3b8;">載入中...</span>
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

      <!-- 右上角登出按鈕 -->
      <div class="floating-logout-button">
        <a-button 
          class="logout-button" 
          size="large"
          @click="handleLogout"
        >
          <LogoutOutlined />
          <span>登出</span>
        </a-button>
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
const role = ref('');
const accountId = ref('');
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
      role.value = userData.role || '';
      accountId.value = userData.accountId || userData.employeeId || '';
      
      // 儲存到 localStorage（選用）
      localStorage.setItem('username', username.value);
      localStorage.setItem('userEmail', userEmail.value);
      localStorage.setItem('role', role.value);
      localStorage.setItem('accountId', accountId.value);
      
      console.log('使用者資訊:', { 
        username: username.value, 
        userEmail: userEmail.value,
        role: role.value,
        accountId: accountId.value
      });
    } else {
      throw new Error('無法解析使用者資訊');
    }
    
  } catch (error) {
    console.error('取得使用者資訊失敗:', error);
    
    // 嘗試從 localStorage 讀取
    const cachedUsername = localStorage.getItem('username');
    const cachedEmail = localStorage.getItem('userEmail');
    const cachedRole = localStorage.getItem('role');
    const cachedAccountId = localStorage.getItem('accountId');
    
    if (cachedUsername) {
      username.value = cachedUsername;
      userEmail.value = cachedEmail || '';
      role.value = cachedRole || '';
      accountId.value = cachedAccountId || '';
      console.log('使用快取的使用者資訊');
    } else {
      // 使用假資料作為後備
      username.value = '王小明';
      userEmail.value = 'wang.xiaoming@company.com';
      role.value = 'admin';
      accountId.value = 'A12345';
      message.warning('無法取得使用者資訊，使用預設資料');
    }
  } finally {
    loadingUserInfo.value = false;
  }
};

const handleLogout = () => {
  message.success('登出成功！');
  
  // 清除登入狀態
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  localStorage.removeItem('userEmail');
  localStorage.removeItem('role');
  localStorage.removeItem('accountId');
  
  // 導向登入頁
  router.push('/login');
};

// 取得角色樣式
const getRoleClass = (roleValue) => {
  const roleMap = {
    'admin': 'role-admin',
    'manager': 'role-manager',
    'user': 'role-user',
  };
  return roleMap[roleValue] || 'role-default';
};

// 取得角色標籤
const getRoleLabel = (roleValue) => {
  const labelMap = {
    'admin': '管理員',
    'manager': '管理者',
    'user': '一般使用者',
  };
  return labelMap[roleValue] || '使用者';
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

/* 右上角登出按鈕 */
.floating-logout-button {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 1000;
}

.logout-button {
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

.logout-button:hover {
  background: #fef2f2 !important;
  border-color: #fca5a5 !important;
  color: #dc2626 !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15);
}

/* 使用者資訊卡片 */
.user-info-card {
  background: #1e293b;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  border: 1px solid rgba(148, 163, 184, 0.1);
}

.user-info-card.loading {
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.user-avatar .anticon {
  font-size: 24px;
  color: white;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.user-account-id {
  font-size: 13px;
  color: #94a3b8;
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.user-role-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.user-role-badge.role-admin {
  background: #ef4444;
  color: white;
}

.user-role-badge.role-manager {
  background: #f59e0b;
  color: white;
}

.user-role-badge.role-user {
  background: #10b981;
  color: white;
}

.user-role-badge.role-default {
  background: #6b7280;
  color: white;
}

.user-email {
  font-size: 12px;
  color: #cbd5e1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .floating-logout-button {
    top: 16px;
    right: 16px;
  }
}
</style>