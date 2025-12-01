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

      <!-- 浮動登出按鈕 -->
      <a-button 
        @click="handleLogout"
        class="floating-logout-button"
        size="large"
      >
        <template #icon>
          <LogoutOutlined />
        </template>
        登出
      </a-button>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, markRaw } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  BarChartOutlined,
  TeamOutlined,
  AppstoreOutlined,
  MonitorOutlined,
  FileTextOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue';
import Overview from '../components/Overview.vue';
import UserManagement from '../components/UserManagement.vue';
import FeatureManagement from '../components/FeatureManagement.vue';
import JobManagement from '../components/JobManagement.vue';
import Audit from '../components/Audit.vue';

const router = useRouter();
const selectedKeys = ref(['overview']);

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

import { logout } from '../utils/auth';

const handleLogout = async () => {
  try {
    await logout();
    message.success('登出成功！');
    router.push('/login');
  } catch (error) {
    console.error('登出失敗:', error);
    message.error('登出失敗，請重試');
  }
};
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

/* 浮動登出按鈕 */
.floating-logout-button {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 1000;
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
</style>