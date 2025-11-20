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
            <a-button type="primary" ghost @click="showAddUserModal(record)">
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
                  <!-- <span style="color: #ef4444; text-decoration: underline wavy"> -->
                    {{ user.email }}
                  <!-- </span> -->
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
              <!-- <span style="color: #ef4444; text-decoration: underline wavy"> -->
                {{ record.email }}
              <!-- </span> -->
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { 
  EditOutlined,
  SearchOutlined
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';

// Modal 控制
const featureModalVisible = ref(false);
const userModalVisible = ref(false);
const isEditMode = ref(false);

// 當前編輯的功能
const currentFeature = ref(null);

// 功能表單
const featureForm = ref({
  featureName: '',
  description: '',
  enabled: true
});

// 使用者搜尋
const userSearchText = ref('');
const selectedUserKeys = ref([]);

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
  { title: 'email', dataIndex: 'email', key: 'email', width: 250 }
];

// 功能資料
const featureData = ref([
  {
    key: '1',
    featureName: 'VESA 轉換',
    description: 'VESA',
    enabled: true,
    users: [
      { key: 'u1', customerId: 'NVT00120', username: 'Amy', email: 'Amy@example.com' },
      { key: 'u2', customerId: 'NVT00134', username: 'anna', email: 'anna@example.com' }
    ]
  },
  {
    key: '2',
    featureName: 'BMP tools',
    description: 'BMP 工具',
    enabled: false,
    users: [
      { key: 'u3', customerId: 'NVT03134', username: 'Hailey', email: 'Hailey@example.com' }
    ]
  }
]);

// 所有可用使用者（用於新增）
const allUsers = ref([
  { key: 'u1', customerId: 'NVT00120', username: 'Amy', email: 'Amy@example.com' },
  { key: 'u2', customerId: 'NVT00134', username: 'anna', email: 'anna@example.com' },
  { key: 'u3', customerId: 'NVT03134', username: 'Hailey', email: 'Hailey@example.com' },
  { key: 'u4', customerId: 'NVT00220', username: 'Eric', email: 'Eric@example.com' },
  { key: 'u5', customerId: 'NVT03334', username: 'Hazel', email: 'Hazel@example.com' },
  { key: 'u6', customerId: 'NVT03131', username: 'Er', email: 'Er@example.com' },
  { key: 'u7', customerId: 'NVT023221', username: 'NY', email: 'NY@example.com' },
  { key: 'u8', customerId: 'NVT02131', username: 'Angela', email: 'Angela@example.com' }
]);

// 篩選後的可用使用者
const filteredAvailableUsers = computed(() => {
  if (!userSearchText.value) return allUsers.value;
  return allUsers.value.filter(user =>
    user.username.toLowerCase().includes(userSearchText.value.toLowerCase())
  );
});

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
const handleFeatureSubmit = () => {
  if (!featureForm.value.featureName || !featureForm.value.description) {
    message.error('請填寫所有必填欄位');
    return;
  }

  if (isEditMode.value) {
    // 更新功能
    Object.assign(currentFeature.value, featureForm.value);
    message.success('功能更新成功！');
  } else {
    // 新增功能
    const newFeature = {
      key: Date.now().toString(),
      ...featureForm.value,
      users: []
    };
    featureData.value.push(newFeature);
    message.success('功能新增成功！');
  }

  featureModalVisible.value = false;
};

// 取消功能表單
const handleFeatureCancel = () => {
  featureModalVisible.value = false;
};

// 啟用/停用狀態變更
const handleStatusChange = (record) => {
  const status = record.enabled ? '啟用' : '停用';
  message.success(`功能「${record.featureName}」已${status}`);
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
const handleBatchAdd = () => {
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

  currentFeature.value.users.push(...newUsers);
  message.success(`成功新增 ${newUsers.length} 位使用者`);
  
  selectedUserKeys.value = [];
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