<!-- FeatureManagement.vue -->
<template>
  <div class="content-wrapper">
    <h1 class="page-title">功能管理</h1>

    <!-- 新增功能按鈕與 Azure AD 登入按鈕 -->
    <div class="action-bar">
      <a-button type="primary" @click="showAddFeatureModal" size="large">
        新增功能
      </a-button>
      
      <!-- Azure AD 登入/登出按鈕 -->
      <a-button 
        v-if="!isAuthenticated" 
        type="default" 
        @click="handleAzureLogin" 
        size="large"
        :loading="isAuthenticating"
      >
        <template #icon>
          <LoginOutlined />
        </template>
        Azure AD 登入
      </a-button>
      
      <a-dropdown v-else>
        <a-button type="default" size="large">
          <UserOutlined />
          {{ userDisplayName }}
          <DownOutlined />
        </a-button>
        <template #overlay>
          <a-menu>
            <a-menu-item key="profile">
              <span>{{ userEmail }}</span>
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item key="logout" @click="handleAzureLogout">
              <LogoutOutlined />
              登出
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>

    <!-- 驗證錯誤提示 -->
    <a-alert
      v-if="authError"
      :message="authError"
      type="error"
      closable
      @close="authError = ''"
      style="margin-bottom: 16px"
    />

    <!-- 功能列表表格 -->
    <a-card class="table-card">
      <a-table
        :columns="featureColumns"
        :data-source="featureData"
        :pagination="false"
        :scroll="{ y: 'calc(100vh - 350px)' }"
        :expandedRowKeys="expandedRowKeys"
        @expand="handleExpand"
        :expandRowByClick="true"
        :loading="tableLoading"
      >
        <template #bodyCell="{ column, record }">
          <!-- 編輯按鈕 -->
          <template v-if="column.key === 'edit'">
            <a-button type="text" @click="handleEdit(record)">
              <EditOutlined style="font-size: 18px" />
            </a-button>
          </template>

          <!-- 啟用/停用開關 -->
          <template v-if="column.key === 'status'">
            <a-switch
              v-model:checked="record.enabled"
              @change="handleStatusChange(record)"
              checked-children="啟用"
              un-checked-children="停用"
            />
          </template>

          <!-- 新增使用者按鈕 -->
          <template v-if="column.key === 'action'">
            <a-button
              type="primary"
              ghost
              @click.stop="showAddUserModal(record)"
            >
              新增使用者
            </a-button>
          </template>
        </template>

        <!-- 展開顯示使用者列表 -->
        <template #expandedRowRender="{ record }">
          <div class="expanded-user-section">
            <h4 class="user-list-title">功能名稱: {{ record.featureName }}</h4>
            <a-table
              :columns="userColumns"
              :data-source="record.users"
              :pagination="false"
              size="small"
              class="user-table"
            >
              <template #bodyCell="{ column, record: user }">
                <template v-if="column.key === 'email'">
                  <span style="color: #ef4444; text-decoration: underline wavy">
                    {{ user.email }}
                  </span>
                </template>
              </template>
            </a-table>
          </div>
        </template>
      </a-table>
    </a-card>

    <!-- 新增/編輯功能 Modal -->
    <a-modal
      v-model:open="featureModalVisible"
      :title="isEditMode ? '編輯功能' : '新增功能'"
      @ok="handleFeatureSubmit"
      @cancel="handleFeatureCancel"
      width="700px"
      :confirmLoading="modalLoading"
    >
      <a-form layout="vertical" :model="featureForm">
        <a-form-item label="功能名稱" required>
          <a-input
            v-model:value="featureForm.featureName"
            placeholder="請輸入功能名稱"
          />
        </a-form-item>
        <a-form-item label="功能描述" required>
          <a-input
            v-model:value="featureForm.description"
            placeholder="請輸入功能描述"
          />
        </a-form-item>
        <a-form-item label="啟用/停用" required>
          <a-switch
            v-model:checked="featureForm.enabled"
            checked-children="啟用"
            un-checked-children="停用"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 新增使用者 Modal -->
    <a-modal
      v-model:open="userModalVisible"
      title="新增使用者"
      @ok="handleUserSubmit"
      @cancel="handleUserCancel"
      width="900px"
    >
      <div class="user-modal-content">
        <div class="modal-header">
          <h3>功能名稱: {{ currentFeature?.featureName }}</h3>
          <a-input
            v-model:value="userSearchText"
            placeholder="Username"
            style="width: 250px"
            @input="handleUserSearch"
          >
            <template #prefix>
              <SearchOutlined />
            </template>
          </a-input>
          <a-button type="primary" @click="handleBatchAdd"> 新增 </a-button>
        </div>

        <!-- 使用者列表 -->
        <a-table
          :columns="userColumns"
          :data-source="filteredAvailableUsers"
          :pagination="false"
          :scroll="{ y: 400 }"
          :row-selection="{
            selectedRowKeys: selectedUserKeys,
            onChange: onUserSelectChange,
          }"
          class="available-users-table"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'email'">
              <span style="color: #ef4444; text-decoration: underline wavy">
                {{ record.email }}
              </span>
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { 
  EditOutlined, 
  SearchOutlined,
  LoginOutlined,
  LogoutOutlined,
  UserOutlined,
  DownOutlined
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { PublicClientApplication } from '@azure/msal-browser';
import { api } from '../utils/api';
import { getAccessToken } from '../utils/auth';

// ============================================
// MSAL 配置
// ============================================

const msalConfig = {
  auth: {
    clientId: 'YOUR_CLIENT_ID', // 替換為你的 Azure AD Client ID
    authority: 'https://login.microsoftonline.com/YOUR_TENANT_ID', // 替換為你的 Tenant ID
    redirectUri: window.location.origin, // 重定向 URI
  },
  cache: {
    cacheLocation: 'localStorage', // 使用 localStorage 保存 token
    storeAuthStateInCookie: false,
  },
};

const loginRequest = {
  scopes: ['User.Read', 'openid', 'profile', 'email'],
};

// MSAL 實例
let msalInstance = null;

// ============================================
// Azure AD 認證狀態
// ============================================

const isAuthenticated = ref(false);
const isAuthenticating = ref(false);
const authError = ref('');
const userDisplayName = ref('');
const userEmail = ref('');
const accessToken = ref('');

// ============================================
// Modal 控制
// ============================================

const featureModalVisible = ref(false);
const userModalVisible = ref(false);
const isEditMode = ref(false);
const currentFeature = ref(null);

// Loading 狀態
const tableLoading = ref(false);
const modalLoading = ref(false);

// 功能表單
const featureForm = ref({
  featureName: '',
  description: '',
  enabled: true,
});

// 使用者搜尋
const userSearchText = ref('');
const selectedUserKeys = ref([]);
const expandedRowKeys = ref([]);

// ============================================
// 表格欄位配置
// ============================================

const featureColumns = [
  { title: '', key: 'edit', width: 60, align: 'center' },
  { title: 'Feature_name', dataIndex: 'featureName', key: 'featureName', width: 200 },
  { title: '描述', dataIndex: 'description', key: 'description', width: 200 },
  { title: '啟用', key: 'status', width: 120 },
  { title: '', key: 'action', width: 150 },
];

const userColumns = [
  { title: 'customer_ID', dataIndex: 'customerId', key: 'customerId', width: 150 },
  { title: 'Username', dataIndex: 'username', key: 'username', width: 150 },
  { title: 'email', dataIndex: 'email', key: 'email', width: 200 },
  { title: '狀態', key: 'status', width: 120, align: 'center' },
];

const featureData = ref([]);
const allUsers = ref([]);

const filteredAvailableUsers = computed(() => {
  if (!currentFeature.value) return [];
  const existingUserKeys = currentFeature.value.users.map((u) => u.key);
  let availableUsers = allUsers.value.filter(
    (user) => !existingUserKeys.includes(user.key)
  );
  if (userSearchText.value) {
    availableUsers = availableUsers.filter((user) =>
      user.username.toLowerCase().includes(userSearchText.value.toLowerCase())
    );
  }
  return availableUsers;
});

// ============================================
// MSAL 認證函數
// ============================================

// 初始化 MSAL
const initializeMsal = async () => {
  try {
    msalInstance = new PublicClientApplication(msalConfig);
    await msalInstance.initialize();
    
    // 處理重定向回來的回應
    const response = await msalInstance.handleRedirectPromise();
    if (response) {
      await handleAzureLoginSuccess(response);
    } else {
      // 檢查是否已有使用者登入
      const accounts = msalInstance.getAllAccounts();
      if (accounts.length > 0) {
        isAuthenticated.value = true;
        userDisplayName.value = accounts[0].name || accounts[0].username;
        userEmail.value = accounts[0].username;
        
        // 靜默獲取 token
        try {
          const tokenResponse = await msalInstance.acquireTokenSilent({
            ...loginRequest,
            account: accounts[0],
          });
          accessToken.value = tokenResponse.accessToken;
          message.success(`歡迎回來，${userDisplayName.value}`);
        } catch (error) {
          console.error('靜默獲取 token 失敗:', error);
        }
      }
    }
  } catch (error) {
    console.error('MSAL 初始化錯誤:', error);
    authError.value = 'Azure AD 服務初始化失敗，請重新整理頁面';
  }
};

// Azure AD 登入
const handleAzureLogin = async () => {
  if (!msalInstance) {
    authError.value = 'MSAL 尚未初始化';
    return;
  }

  isAuthenticating.value = true;
  authError.value = '';

  try {
    // 使用重定向方式登入
    await msalInstance.loginRedirect(loginRequest);
  } catch (error) {
    console.error('Azure AD 登入錯誤:', error);
    authError.value = `登入失敗: ${error.message}`;
    isAuthenticating.value = false;
  }
};

// 處理登入成功
const handleAzureLoginSuccess = async (response) => {
  try {
    isAuthenticated.value = true;
    accessToken.value = response.accessToken;
    
    const account = response.account;
    userDisplayName.value = account.name || account.username;
    userEmail.value = account.username;

    message.success(`登入成功！歡迎 ${userDisplayName.value}`);
    
    // 登入成功後重新載入資料
    await Promise.all([fetchFeatures(), fetchAllUsers()]);
  } catch (error) {
    console.error('處理登入回應錯誤:', error);
    authError.value = '處理登入資訊失敗';
  } finally {
    isAuthenticating.value = false;
  }
};

// Azure AD 登出
const handleAzureLogout = async () => {
  if (!msalInstance) return;

  try {
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      await msalInstance.logoutRedirect({
        account: accounts[0],
      });
    }
  } catch (error) {
    console.error('登出錯誤:', error);
    message.error('登出失敗');
  }
};

// 獲取當前的 Access Token（用於 API 呼叫）
const getCurrentAccessToken = async () => {
  if (!msalInstance || !isAuthenticated.value) {
    return null;
  }

  const accounts = msalInstance.getAllAccounts();
  if (accounts.length === 0) {
    return null;
  }

  try {
    const response = await msalInstance.acquireTokenSilent({
      ...loginRequest,
      account: accounts[0],
    });
    return response.accessToken;
  } catch (error) {
    console.error('獲取 token 失敗:', error);
    // 如果靜默獲取失敗，嘗試重新登入
    await msalInstance.acquireTokenRedirect(loginRequest);
    return null;
  }
};

// ============================================
// API 呼叫函數
// ============================================

const fetchFeatures = async () => {
  tableLoading.value = true;
  try {
    const token = await getCurrentAccessToken();
    const response = await api.get('/features', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    featureData.value = response.data.data.map((feature) => ({
      key: feature.id.toString(),
      featureName: feature.featureName,
      description: feature.description,
      enabled: feature.enabled,
      users: feature.users || [],
    }));

    message.success('功能列表載入成功');
  } catch (error) {
    console.error('取得功能列表失敗:', error);
    message.error('載入功能列表失敗，請重試');

    // 使用假資料作為備用
    featureData.value = [
      {
        key: '1',
        featureName: 'VESA 轉換',
        description: 'VESA',
        enabled: true,
        users: [
          {
            key: 'u1',
            customerId: 'NVT00120',
            username: 'Amy',
            email: 'Amy@example.com',
            enabled: true,
          },
        ],
      },
    ];
  } finally {
    tableLoading.value = false;
  }
};

const fetchAllUsers = async () => {
  try {
    const token = await getCurrentAccessToken();
    const response = await api.get('/users/all', {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    allUsers.value = response.data.data.map((user) => ({
      key: user.id.toString(),
      customerId: user.customerId,
      username: user.username,
      email: user.email,
    }));
  } catch (error) {
    console.error('取得使用者列表失敗:', error);
    allUsers.value = [
      { key: 'u1', customerId: 'NVT00120', username: 'Amy', email: 'Amy@example.com' },
      { key: 'u2', customerId: 'NVT00134', username: 'anna', email: 'anna@example.com' },
    ];
  }
};

const createFeature = async (featureData) => {
  const token = await getCurrentAccessToken();
  const response = await api.post('/features', featureData, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  return response.data;
};

const updateFeature = async (featureId, featureData) => {
  const token = await getCurrentAccessToken();
  const response = await api.put(`/features/${featureId}`, featureData, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  return response.data;
};

const updateFeatureStatus = async (featureId, enabled) => {
  const token = await getCurrentAccessToken();
  await api.patch(`/features/${featureId}/status`, { enabled }, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
};

const addUsersToFeature = async (featureId, userIds) => {
  const token = await getCurrentAccessToken();
  await api.post(`/features/${featureId}/users`, { userIds }, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
};

// ============================================
// 生命週期
// ============================================

onMounted(async () => {
  // 初始化 MSAL
  await initializeMsal();
  
  // 載入資料
  await Promise.all([fetchFeatures(), fetchAllUsers()]);
});

// ============================================
// 事件處理函數（保持原有功能）
// ============================================

const showAddFeatureModal = () => {
  isEditMode.value = false;
  featureForm.value = { featureName: '', description: '', enabled: true };
  featureModalVisible.value = true;
};

const handleEdit = (record) => {
  isEditMode.value = true;
  currentFeature.value = record;
  featureForm.value = {
    featureName: record.featureName,
    description: record.description,
    enabled: record.enabled,
  };
  featureModalVisible.value = true;
};

const handleFeatureSubmit = async () => {
  if (!featureForm.value.featureName || !featureForm.value.description) {
    message.error('請填寫所有必填欄位');
    return;
  }

  modalLoading.value = true;
  try {
    if (isEditMode.value) {
      await updateFeature(currentFeature.value.key, featureForm.value);
      Object.assign(currentFeature.value, featureForm.value);
      message.success('功能更新成功！');
    } else {
      const result = await createFeature(featureForm.value);
      const newFeature = {
        key: result.data.id.toString(),
        ...featureForm.value,
        users: [],
      };
      featureData.value.push(newFeature);
      message.success('功能新增成功！');
    }
    featureModalVisible.value = false;
  } catch (error) {
    message.error(isEditMode.value ? '功能更新失敗' : '功能新增失敗');
  } finally {
    modalLoading.value = false;
  }
};

const handleFeatureCancel = () => {
  featureModalVisible.value = false;
};

const handleStatusChange = async (record) => {
  try {
    await updateFeatureStatus(record.key, record.enabled);
    const status = record.enabled ? '啟用' : '停用';
    message.success(`功能「${record.featureName}」已${status}`);
  } catch (error) {
    record.enabled = !record.enabled;
    message.error('更新狀態失敗');
  }
};

const showAddUserModal = (record) => {
  currentFeature.value = record;
  selectedUserKeys.value = [];
  userSearchText.value = '';
  userModalVisible.value = true;
};

const handleUserSearch = () => {};

const onUserSelectChange = (selectedKeys) => {
  selectedUserKeys.value = selectedKeys;
};

const handleBatchAdd = async () => {
  if (selectedUserKeys.value.length === 0) {
    message.warning('請至少選擇一位使用者');
    return;
  }

  const selectedUsers = allUsers.value.filter((user) =>
    selectedUserKeys.value.includes(user.key)
  );

  const existingKeys = currentFeature.value.users.map((u) => u.key);
  const newUsers = selectedUsers.filter((user) => !existingKeys.includes(user.key));

  if (newUsers.length === 0) {
    message.warning('所選使用者已存在');
    return;
  }

  modalLoading.value = true;
  try {
    const userIds = newUsers.map((u) => u.key);
    await addUsersToFeature(currentFeature.value.key, userIds);

    const usersToAdd = newUsers.map((user) => ({ ...user, enabled: true }));
    currentFeature.value.users.push(...usersToAdd);
    message.success(`成功新增 ${newUsers.length} 位使用者`);
    selectedUserKeys.value = [];
  } catch (error) {
    message.error('新增使用者失敗');
  } finally {
    modalLoading.value = false;
  }
};

const handleUserSubmit = () => {
  handleBatchAdd();
  userModalVisible.value = false;
};

const handleUserCancel = () => {
  userModalVisible.value = false;
  selectedUserKeys.value = [];
};

const handleExpand = (expanded, record) => {
  expandedRowKeys.value = expanded ? [record.key] : [];
};
</script>

<style scoped>
.content-wrapper {
  padding: 32px;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 24px;
  flex-shrink: 0;
}

.action-bar {
  margin-bottom: 24px;
  flex-shrink: 0;
  display: flex;
  gap: 12px;
}

.table-card {
  flex: 1;
  overflow: hidden;
}

.table-card :deep(.ant-card-body) {
  height: 100%;
  padding: 0;
}

.expanded-user-section {
  background: #f9fafb;
  padding: 24px;
}

.user-list-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.user-table {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.user-table :deep(.ant-table-thead > tr > th) {
  background: #f3f4f6;
  font-weight: 600;
}

.user-modal-content {
  padding-top: 20px;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.modal-header h3 {
  flex: 1;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.available-users-table {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.available-users-table :deep(.ant-table-thead > tr > th) {
  background: #f3f4f6;
  font-weight: 600;
}

:deep(.ant-table-tbody > tr) {
  cursor: pointer;
}

:deep(.ant-table-tbody > tr:nth-child(even)) {
  background-color: #f9fafb;
}

:deep(.ant-table-tbody > tr:hover) {
  background-color: #e0f2fe !important;
}

:deep(.ant-table-expanded-row > td) {
  padding: 0 !important;
  background: #ffffff !important;
}

:deep(.ant-table-body)::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

:deep(.ant-table-body)::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

:deep(.ant-table-body)::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

:deep(.ant-table-body)::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>