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

      <!-- 右上角使用者下拉選單 -->
      <div class="floating-user-dropdown">
        <a-dropdown placement="bottomRight" :trigger="['click']">
          <a-button class="user-dropdown-button" size="large" v-if="!loadingUserInfo">
            <div class="user-button-content">
              <div class="user-avatar-small">
                <UserOutlined />
              </div>
              <div class="user-button-info">
                <div class="user-button-name">{{ username || '使用者' }}</div>
                <div class="user-button-role">{{ getRoleLabel(role) }}</div>
              </div>
              <DownOutlined class="dropdown-icon" />
            </div>
          </a-button>
          <a-button class="user-dropdown-button loading" size="large" v-else>
            <a-spin size="small" />
            <span style="margin-left: 8px;">載入中...</span>
          </a-button>
          
          <template #overlay>
            <a-menu class="user-dropdown-menu">
              <!-- 使用者資訊區塊 -->
              <div class="user-info-section">
                <div class="user-avatar-large">
                  <UserOutlined />
                </div>
                <div class="user-info-details">
                  <div class="user-info-name">{{ username || '使用者' }}</div>
                  <div class="user-info-meta">
                    <span class="user-info-account-id">{{ accountId || '-' }}</span>
                    <span class="user-role-badge" :class="getRoleClass(role)">
                      {{ getRoleLabel(role) }}
                    </span>
                  </div>
                  <div class="user-info-email">{{ userEmail || '-' }}</div>
                </div>
              </div>
              
              <a-menu-divider />
              
              <!-- 登出選項 -->
              <a-menu-item key="logout" @click="handleLogout" class="logout-menu-item">
                <LogoutOutlined />
                <span>登出</span>
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

/* 右上角使用者下拉選單 */
.floating-user-dropdown {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 1000;
}

/* 使用者下拉按鈕 */
.user-dropdown-button {
  height: 52px;
  padding: 0 16px;
  background: white;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.user-dropdown-button:hover {
  background: #f9fafb !important;
  border-color: #d1d5db !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.user-dropdown-button.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
}

.user-button-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar-small {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-avatar-small .anticon {
  font-size: 18px;
  color: white;
}

.user-button-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.user-button-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.2;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-button-role {
  font-size: 11px;
  color: #6b7280;
  line-height: 1.2;
}

.dropdown-icon {
  font-size: 12px;
  color: #9ca3af;
  margin-left: 4px;
}

/* 下拉選單 */
.user-dropdown-menu {
  min-width: 280px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 8px;
  margin-top: 8px;
}

/* 使用者資訊區塊 */
.user-info-section {
  padding: 16px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.user-avatar-large {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.user-avatar-large .anticon {
  font-size: 24px;
  color: white;
}

.user-info-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.user-info-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-info-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.user-info-account-id {
  font-size: 12px;
  color: #6b7280;
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.user-role-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.user-role-badge.role-admin {
  background: #fee2e2;
  color: #dc2626;
}

.user-role-badge.role-manager {
  background: #fef3c7;
  color: #d97706;
}

.user-role-badge.role-user {
  background: #d1fae5;
  color: #059669;
}

.user-role-badge.role-default {
  background: #f3f4f6;
  color: #6b7280;
}

.user-info-email {
  font-size: 12px;
  color: #9ca3af;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 登出選項 */
.logout-menu-item {
  color: #dc2626 !important;
  font-weight: 500;
  border-radius: 8px;
  margin-top: 4px;
}

.logout-menu-item:hover {
  background: #fef2f2 !important;
}

.logout-menu-item .anticon {
  margin-right: 8px;
}

/* 選單分隔線 */
:deep(.ant-dropdown-menu-item-divider) {
  margin: 8px 0;
  background-color: #e5e7eb;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .floating-user-dropdown {
    top: 16px;
    right: 16px;
  }

  .user-button-name {
    max-width: 80px;
  }

  .user-dropdown-menu {
    min-width: 260px;
  }
}
</style>