<!-- FeatureManagement.vue -->
<template>
  <div class="content-wrapper">
    <h1 class="page-title">功能管理</h1>
    
    <!-- 新增功能按鈕 -->
    <div class="action-bar">
      <a-button type="primary" @click="showAddFeatureModal" size="large">
        新增功能
      </a-button>
    </div>

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
          <a-input v-model:value="featureForm.featureName" placeholder="請輸入功能名稱" />
        </a-form-item>
        <a-form-item label="功能描述" required>
          <a-input v-model:value="featureForm.description" placeholder="請輸入功能描述" />
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
          <a-button type="primary" @click="handleBatchAdd">
            新增
          </a-button>
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
  SearchOutlined
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { api } from '../utils/api'; // 引入 API 工具

// Modal 控制
const featureModalVisible = ref(false);
const userModalVisible = ref(false);
const isEditMode = ref(false);

// 當前編輯的功能
const currentFeature = ref(null);

// Loading 狀態
const tableLoading = ref(false);
const modalLoading = ref(false);

// 功能表單
const featureForm = ref({
  featureName: '',
  description: '',
  enabled: true
});

// 使用者搜尋
const userSearchText = ref('');
const selectedUserKeys = ref([]);
const expandedRowKeys = ref([]);

// 功能表格欄位
const featureColumns = [
  { 
    title: '', 
    key: 'edit',
    width: 60,
    align: 'center'
  },
  { 
    title: 'Feature_name', 
    dataIndex: 'featureName', 
    key: 'featureName',
    width: 200
  },
  { 
    title: '描述', 
    dataIndex: 'description', 
    key: 'description',
    width: 200
  },
  { 
    title: '啟用', 
    key: 'status',
    width: 120
  },
  { 
    title: '', 
    key: 'action',
    width: 150
  }
];

// 使用者表格欄位
const userColumns = [
  { title: 'customer_ID', dataIndex: 'customerId', key: 'customerId', width: 150 },
  { title: 'Username', dataIndex: 'username', key: 'username', width: 150 },
  { title: 'email', dataIndex: 'email', key: 'email', width: 200 },
  { title: '狀態', key: 'status', width: 120, align: 'center' }
];

// 功能資料（從 API 取得）
const featureData = ref([]);

// 所有可用使用者（從 API 取得）
const allUsers = ref([]);

// 篩選後的可用使用者（排除已加入該功能的使用者）
const filteredAvailableUsers = computed(() => {
  if (!currentFeature.value) return [];
  
  // 獲取已加入該功能的使用者 key
  const existingUserKeys = currentFeature.value.users.map(u => u.key);
  
  // 過濾掉已加入的使用者
  let availableUsers = allUsers.value.filter(user => 
    !existingUserKeys.includes(user.key)
  );
  
  // 如果有搜尋文字，再進行搜尋篩選
  if (userSearchText.value) {
    availableUsers = availableUsers.filter(user =>
      user.username.toLowerCase().includes(userSearchText.value.toLowerCase())
    );
  }
  
  return availableUsers;
});

// ============================================
// API 呼叫函數
// ============================================

// 取得功能列表
const fetchFeatures = async () => {
  tableLoading.value = true;
  try {
    const response = await api.get('/features');

    // 處理 API 回傳的資料格式
    // 假設 API 回傳格式：
    // {
    //   success: true,
    //   data: [
    //     {
    //       id: 1,
    //       featureName: 'VESA 轉換',
    //       description: 'VESA',
    //       enabled: true,
    //       users: [...]
    //     }
    //   ]
    // }
    
    featureData.value = response.data.data.map(feature => ({
      key: feature.id.toString(),
      featureName: feature.featureName,
      description: feature.description,
      enabled: feature.enabled,
      users: feature.users || []
    }));
    
    message.success('功能列表載入成功');
  } catch (error) {
    console.error('取得功能列表失敗:', error);
    message.error('載入功能列表失敗，請重試');
    
    // 使用假資料作為備用（開發時使用）
    featureData.value = [
      {
        key: '1',
        featureName: 'VESA 轉換',
        description: 'VESA',
        enabled: true,
        users: [
          { key: 'u1', customerId: 'NVT00120', username: 'Amy', email: 'Amy@example.com', enabled: true },
          { key: 'u2', customerId: 'NVT00134', username: 'anna', email: 'anna@example.com', enabled: true }
        ]
      }
    ];
  } finally {
    tableLoading.value = false;
  }
};

// 取得所有可用使用者
const fetchAllUsers = async () => {
  try {
    const response = await api.get('/users/all');
    
    // 假設 API 回傳格式：
    // {
    //   success: true,
    //   data: [
    //     {
    //       id: 1,
    //       customerId: 'NVT00120',
    //       username: 'Amy',
    //       email: 'Amy@example.com'
    //     }
    //   ]
    // }
    
    allUsers.value = response.data.data.map(user => ({
      key: user.id.toString(),
      customerId: user.customerId,
      username: user.username,
      email: user.email
    }));
  } catch (error) {
    console.error('取得使用者列表失敗:', error);
    
    // 使用假資料作為備用
    allUsers.value = [
      { key: 'u1', customerId: 'NVT00120', username: 'Amy', email: 'Amy@example.com' },
      { key: 'u2', customerId: 'NVT00134', username: 'anna', email: 'anna@example.com' },
      { key: 'u3', customerId: 'NVT03134', username: 'Hailey', email: 'Hailey@example.com' },
      { key: 'u4', customerId: 'NVT00220', username: 'Eric', email: 'Eric@example.com' },
      { key: 'u5', customerId: 'NVT03334', username: 'Hazel', email: 'Hazel@example.com' },
      { key: 'u6', customerId: 'NVT03131', username: 'Er', email: 'Er@example.com' },
      { key: 'u7', customerId: 'NVT023221', username: 'NY', email: 'NY@example.com' },
      { key: 'u8', customerId: 'NVT02131', username: 'Angela', email: 'Angela@example.com' }
    ];
  }
};

// 新增功能到後端
const createFeature = async (featureData) => {
  try {
    const response = await api.post('/features', {
      featureName: featureData.featureName,
      description: featureData.description,
      enabled: featureData.enabled
    });
    
    return response.data;
  } catch (error) {
    console.error('新增功能失敗:', error);
    throw error;
  }
};

// 更新功能到後端
const updateFeature = async (featureId, featureData) => {
  try {
    const response = await api.put(`/features/${featureId}`, {
      featureName: featureData.featureName,
      description: featureData.description,
      enabled: featureData.enabled
    });
    
    return response.data;
  } catch (error) {
    console.error('更新功能失敗:', error);
    throw error;
  }
};

// 更新功能狀態
const updateFeatureStatus = async (featureId, enabled) => {
  try {
    await api.patch(`/features/${featureId}/status`, {
      enabled: enabled
    });
  } catch (error) {
    console.error('更新功能狀態失敗:', error);
    throw error;
  }
};

// 新增使用者到功能
const addUsersToFeature = async (featureId, userIds) => {
  try {
    await api.post(`/features/${featureId}/users`, {
      userIds: userIds
    });
  } catch (error) {
    console.error('新增使用者失敗:', error);
    throw error;
  }
};

// 更新使用者在功能中的狀態
const updateUserFeatureStatus = async (featureId, userId, enabled) => {
  try {
    await api.patch(`/features/${featureId}/users/${userId}`, {
      enabled: enabled
    });
  } catch (error) {
    console.error('更新使用者狀態失敗:', error);
    throw error;
  }
};

// ============================================
// 組件生命週期
// ============================================

onMounted(async () => {
  // 頁面載入時取得資料
  await Promise.all([
    fetchFeatures(),
    fetchAllUsers()
  ]);
});

// ============================================
// 事件處理函數
// ============================================

// 顯示新增功能 Modal
const showAddFeatureModal = () => {
  isEditMode.value = false;
  featureForm.value = {
    featureName: '',
    description: '',
    enabled: true
  };
  featureModalVisible.value = true;
};

// 編輯功能
const handleEdit = (record) => {
  isEditMode.value = true;
  currentFeature.value = record;
  featureForm.value = {
    featureName: record.featureName,
    description: record.description,
    enabled: record.enabled
  };
  featureModalVisible.value = true;
};

// 提交功能表單
const handleFeatureSubmit = async () => {
  if (!featureForm.value.featureName || !featureForm.value.description) {
    message.error('請填寫所有必填欄位');
    return;
  }

  modalLoading.value = true;

  try {
    if (isEditMode.value) {
      // 更新功能
      await updateFeature(currentFeature.value.key, featureForm.value);
      Object.assign(currentFeature.value, featureForm.value);
      message.success('功能更新成功！');
    } else {
      // 新增功能
      const result = await createFeature(featureForm.value);
      const newFeature = {
        key: result.data.id.toString(),
        ...featureForm.value,
        users: []
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

// 取消功能表單
const handleFeatureCancel = () => {
  featureModalVisible.value = false;
};

// 啟用/停用狀態變更
const handleStatusChange = async (record) => {
  try {
    await updateFeatureStatus(record.key, record.enabled);
    const status = record.enabled ? '啟用' : '停用';
    message.success(`功能「${record.featureName}」已${status}`);
  } catch (error) {
    // 還原狀態
    record.enabled = !record.enabled;
    message.error('更新狀態失敗');
  }
};

// 顯示新增使用者 Modal
const showAddUserModal = (record) => {
  currentFeature.value = record;
  selectedUserKeys.value = [];
  userSearchText.value = '';
  userModalVisible.value = true;
};

// 使用者搜尋
const handleUserSearch = () => {
  // 搜尋已在 computed 中處理
};

// 使用者選擇變更
const onUserSelectChange = (selectedKeys) => {
  selectedUserKeys.value = selectedKeys;
};

// 批次新增使用者
const handleBatchAdd = async () => {
  if (selectedUserKeys.value.length === 0) {
    message.warning('請至少選擇一位使用者');
    return;
  }

  const selectedUsers = allUsers.value.filter(user =>
    selectedUserKeys.value.includes(user.key)
  );

  // 過濾已存在的使用者
  const existingKeys = currentFeature.value.users.map(u => u.key);
  const newUsers = selectedUsers.filter(user => !existingKeys.includes(user.key));

  if (newUsers.length === 0) {
    message.warning('所選使用者已存在');
    return;
  }

  modalLoading.value = true;

  try {
    // 呼叫 API 新增使用者
    const userIds = newUsers.map(u => u.key);
    await addUsersToFeature(currentFeature.value.key, userIds);

    // 新增使用者時，預設為啟用狀態
    const usersToAdd = newUsers.map(user => ({
      ...user,
      enabled: true
    }));

    currentFeature.value.users.push(...usersToAdd);
    message.success(`成功新增 ${newUsers.length} 位使用者`);
    
    selectedUserKeys.value = [];
  } catch (error) {
    message.error('新增使用者失敗');
  } finally {
    modalLoading.value = false;
  }
};

// 提交使用者新增
const handleUserSubmit = () => {
  handleBatchAdd();
  userModalVisible.value = false;
};

// 取消使用者新增
const handleUserCancel = () => {
  userModalVisible.value = false;
  selectedUserKeys.value = [];
};

// 展開/收合功能
const handleExpand = (expanded, record) => {
  if (expanded) {
    expandedRowKeys.value = [record.key];
  } else {
    expandedRowKeys.value = [];
  }
};

// 使用者狀態變更
const handleUserStatusChange = async (feature, user) => {
  try {
    await updateUserFeatureStatus(feature.key, user.key, user.enabled);
    const status = user.enabled ? '啟用' : '停用';
    message.success(`使用者「${user.username}」在功能「${feature.featureName}」已${status}`);
  } catch (error) {
    // 還原狀態
    user.enabled = !user.enabled;
    message.error('更新使用者狀態失敗');
  }
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
}

.table-card {
  flex: 1;
  overflow: hidden;
}

.table-card :deep(.ant-card-body) {
  height: 100%;
  padding: 0;
}

/* 展開的使用者區塊 */
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

/* Modal 樣式 */
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

/* 表格樣式 */
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

/* 自定義滾動條 */
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