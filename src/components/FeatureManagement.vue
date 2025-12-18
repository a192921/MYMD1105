<template>
  <div class="content-wrapper">
    <h1 class="page-title">功能管理</h1>

    <a-card class="table-card">
      <a-table
        :columns="featureColumns"
        :data-source="featureData"
        :pagination="false"
        :expandedRowKeys="expandedRowKeys"
        @expand="handleExpand"
        :loading="tableLoading"
        :expandRowByClick="true"
      >
        <!-- 功能列表欄位 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-button type="primary" ghost @click.stop="openUserModal(record)">
              授權使用者
            </a-button>
          </template>
        </template>

        <!-- 展開：已授權使用者 -->
        <template #expandedRowRender="{ record: feature }">
          <div class="expanded-section">
            <h4 class="section-title">已授權使用者</h4>
            <a-table
              :columns="authorizedUserColumns"
              :data-source="feature.users"
              :loading="feature.usersLoading"
              size="small"
              :pagination="false"
              class="authorized-users-table"
            >
              <template #bodyCell="{ column, record: user }">
                <!-- Email 特殊樣式 -->
                <template v-if="column.key === 'email'">
                  <span style="color: #3b82f6">{{ user.email }}</span>
                </template>
                
                <!-- 授權狀態：預設為已授權 -->
                <template v-if="column.key === 'status'">
                  <a-space>
                    <a-switch
                      checked
                      size="small"
                      :disabled="true"
                    />
                    <span style="color: #10b981; font-weight: 500;">已授權</span>
                  </a-space>
                </template>
                
                <!-- 收回授權按鈕 -->
                <template v-if="column.key === 'action'">
                  <a-button 
                    type="default"
                    size="small"
                    @click="revokeUser(feature, user)"
                    style="
                      background: #f3f4f6;
                      color: #6b7280;
                      border: none;
                      border-radius: 16px;
                      padding: 4px 16px;
                      font-weight: 500;
                    "
                  >
                    移除
                  </a-button>
                </template>
              </template>
            </a-table>
          </div>
        </template>
      </a-table>
    </a-card>

    <!-- 授權使用者 Modal -->
    <a-modal
      v-model:open="userModalVisible"
      title="授權使用者"
      width="900px"
      @cancel="handleModalCancel"
      :footer="null"
    >
      <div class="modal-content">
        <h3 class="modal-feature-name">功能：{{ currentFeature?.featureName }}</h3>
        
        <a-table
          :columns="allUserColumns"
          :data-source="mappedUsers"
          :pagination="false"
          :scroll="{ y: 400 }"
          class="users-table"
        >
          <template #bodyCell="{ column, record: user }">
            <!-- Email 特殊樣式 -->
            <template v-if="column.key === 'email'">
              <span style="color: #3b82f6">{{ user.email }}</span>
            </template>
            
            <!-- 授權開關 -->
            <template v-if="column.key === 'status'">
              <a-space>
                <a-switch
                  :checked="user.authorized"
                  :loading="user.loading"
                  size="small"
                  @change="(checked) => toggleAuthorize(checked, user)"
                />
                <span 
                  :style="{
                    color: user.authorized ? '#10b981' : '#9ca3af',
                    fontWeight: 500
                  }"
                >
                  {{ user.authorized ? '已授權' : '未授權' }}
                </span>
              </a-space>
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { api } from '../utils/api';

/* ================= 狀態 ================= */
const featureData = ref([]);
const allUsers = ref([]);
const expandedRowKeys = ref([]);
const tableLoading = ref(false);
const userModalVisible = ref(false);
const currentFeature = ref(null);

/* ================= 欄位定義 ================= */
const featureColumns = [
  { title: '功能名稱', dataIndex: 'featureName', key: 'featureName', width: 200 },
  { title: '描述', dataIndex: 'description', key: 'description', width: 300 },
  { title: '', key: 'action', width: 150, align: 'center' }
];

const authorizedUserColumns = [
  { title: 'Customer ID', dataIndex: 'customerId', key: 'customerId', width: 150 },
  { title: 'Username', dataIndex: 'username', key: 'username', width: 150 },
  { title: 'Email', dataIndex: 'email', key: 'email', width: 200 },
  { title: '授權狀態', key: 'status', width: 150, align: 'center' },
  { title: '', key: 'action', width: 100, align: 'center' }
];

const allUserColumns = [
  { title: 'Customer ID', dataIndex: 'customerId', key: 'customerId', width: 150 },
  { title: 'Username', dataIndex: 'username', key: 'username', width: 150 },
  { title: 'Email', dataIndex: 'email', key: 'email', width: 200 },
  { title: '授權狀態', key: 'status', width: 150, align: 'center' }
];

/* ================= 計算屬性：合併授權狀態 ================= */
const mappedUsers = computed(() => {
  if (!currentFeature.value) return [];
  
  // 取得已授權使用者的 ID 列表
  const authorizedIds = currentFeature.value.users.map(u => u.key);
  
  // 為所有使用者加上授權狀態
  return allUsers.value.map(u => ({
    ...u,
    authorized: authorizedIds.includes(u.key),
    loading: false
  }));
});

/* ================= API 呼叫函數 ================= */

// 取得功能列表
const fetchFeatures = async () => {
  tableLoading.value = true;
  try {
    const response = await api.get('/api/admin/features');
    
    console.log('功能列表 API 回應:', response.data);
    
    // 處理不同的回應格式
    let features = [];
    if (response.data && response.data.res && Array.isArray(response.data.res.data)) {
      features = response.data.res.data;
    } else if (response.data && Array.isArray(response.data.data)) {
      features = response.data.data;
    } else if (Array.isArray(response.data)) {
      features = response.data;
    }
    
    featureData.value = features.map(f => ({
      key: f.id?.toString() || f.featureId?.toString(),
      featureName: f.name || f.featureName,
      description: f.description,
      users: [], // 初始為空，展開時才載入
      usersLoading: false
    }));
    
    message.success('功能列表載入成功');
  } catch (error) {
    console.error('載入功能列表失敗:', error);
    
    // 使用假資料
    featureData.value = [
      {
        key: '1',
        featureName: 'VESA 轉換',
        description: 'VESA 相關功能',
        users: [],
        usersLoading: false
      },
      {
        key: '2',
        featureName: '報表匯出',
        description: 'CSV / Excel 匯出',
        users: [],
        usersLoading: false
      }
    ];
  } finally {
    tableLoading.value = false;
  }
};

// 取得功能的已授權使用者列表
const fetchFeatureUsers = async (feature) => {
  feature.usersLoading = true;
  try {
    // API: GET /api/admin/feature/{featureId}/customers
    const response = await api.get(`/api/admin/feature/${feature.key}/customers`);
    
    console.log(`功能 ${feature.featureName} 的使用者:`, response.data);
    
    // 處理不同的回應格式
    let users = [];
    if (response.data && response.data.res && Array.isArray(response.data.res.data)) {
      users = response.data.res.data;
    } else if (response.data && Array.isArray(response.data.data)) {
      users = response.data.data;
    } else if (Array.isArray(response.data)) {
      users = response.data;
    }
    
    // 映射使用者資料，預設授權狀態為 true（已授權）
    feature.users = users.map(u => ({
      key: u.userId || u.account || u.id?.toString(),
      customerId: u.userId || u.account || u.customerId,
      username: u.displayName || u.username || u.name,
      email: u.email || u.mail,
      authorized: true // 預設為已授權
    }));
    
    console.log(`映射後的使用者列表:`, feature.users);
  } catch (error) {
    console.error('載入使用者列表失敗:', error);
    
    // 使用假資料
    feature.users = feature.key === '1'
      ? [
          { key: 'Queena_Wu', customerId: 'Queena_Wu', username: 'Queena', email: 'queena@test.com', authorized: true },
          { key: 'Eric_Lin', customerId: 'Eric_Lin', username: 'Eric', email: 'eric@test.com', authorized: true }
        ]
      : [
          { key: 'Hailey_Chen', customerId: 'Hailey_Chen', username: 'Hailey', email: 'hailey@test.com', authorized: true }
        ];
  } finally {
    feature.usersLoading = false;
  }
};

// 取得所有使用者列表
const fetchAllUsers = async () => {
  try {
    const response = await api.get('/api/admin/users/all');
    
    console.log('所有使用者 API 回應:', response.data);
    
    // 處理不同的回應格式
    let users = [];
    if (response.data && response.data.res && Array.isArray(response.data.res.data)) {
      users = response.data.res.data;
    } else if (response.data && Array.isArray(response.data.data)) {
      users = response.data.data;
    } else if (Array.isArray(response.data)) {
      users = response.data;
    }
    
    allUsers.value = users.map(u => ({
      key: u.userId || u.account || u.id?.toString(),
      customerId: u.userId || u.account || u.customerId,
      username: u.displayName || u.username || u.name,
      email: u.email || u.mail
    }));
  } catch (error) {
    console.error('載入所有使用者失敗:', error);
    
    // 使用假資料
    allUsers.value = [
      { key: 'Queena_Wu', customerId: 'Queena_Wu', username: 'Queena', email: 'queena@test.com' },
      { key: 'Eric_Lin', customerId: 'Eric_Lin', username: 'Eric', email: 'eric@test.com' },
      { key: 'Hailey_Chen', customerId: 'Hailey_Chen', username: 'Hailey', email: 'hailey@test.com' },
      { key: 'Angela_Wang', customerId: 'Angela_Wang', username: 'Angela', email: 'angela@test.com' }
    ];
  }
};

/* ================= 事件處理 ================= */

// 展開/收合功能行
const handleExpand = async (expanded, feature) => {
  if (expanded) {
    expandedRowKeys.value = [feature.key];
    // 展開時載入該功能的已授權使用者
    await fetchFeatureUsers(feature);
  } else {
    expandedRowKeys.value = [];
  }
};

// 打開授權使用者 Modal
const openUserModal = (feature) => {
  currentFeature.value = feature;
  userModalVisible.value = true;
};

// 關閉 Modal
const handleModalCancel = () => {
  userModalVisible.value = false;
  currentFeature.value = null;
};

// 切換授權狀態（在 Modal 中）
const toggleAuthorize = async (checked, user) => {
  const featureId = currentFeature.value.key;
  const customerId = user.customerId;
  
  user.loading = true;
  
  try {
    if (checked) {
      // 授權使用者
      // API: POST /api/admin/features/{featureId}/customers
      await api.post(`/api/admin/features/${featureId}/customers`, [
        {
          account: user.customerId,
          mail: user.email
        }
      ]);
      message.success(`已授權 ${user.username}`);
    } else {
      // 取消授權
      // API: DELETE /api/admin/features/{featureId}/customers/{customerId}
      await api.delete(`/api/admin/features/${featureId}/customers/${customerId}`);
      message.success(`已取消授權 ${user.username}`);
    }
    
    // 重新載入該功能的使用者列表
    await fetchFeatureUsers(currentFeature.value);
  } catch (error) {
    console.error('更新授權失敗:', error);
    message.error('更新授權失敗，請重試');
  } finally {
    user.loading = false;
  }
};

// 收回授權（在展開列表中）
const revokeUser = async (feature, user) => {
  Modal.confirm({
    title: '確認收回授權',
    content: `確定要收回使用者「${user.username}」(${user.email}) 的授權嗎？`,
    okText: '確定收回',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      try {
        // API: DELETE /api/admin/features/{featureId}/customers/{customerId}
        await api.delete(`/api/admin/features/${feature.key}/customers/${user.customerId}`);
        
        message.success(`已收回 ${user.username} 的授權`);
        
        // 重新載入該功能的使用者列表
        await fetchFeatureUsers(feature);
      } catch (error) {
        console.error('收回授權失敗:', error);
        message.error('收回授權失敗，請重試');
      }
    }
  });
};

/* ================= 生命週期 ================= */
onMounted(() => {
  fetchFeatures();
  fetchAllUsers();
});
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
}

.table-card {
  flex: 1;
  overflow: hidden;
}

.table-card :deep(.ant-card-body) {
  height: 100%;
  padding: 0;
}

/* 展開區域樣式 */
.expanded-section {
  background: #f9fafb;
  padding: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.authorized-users-table {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.authorized-users-table :deep(.ant-table-thead > tr > th) {
  background: #f3f4f6;
  font-weight: 600;
}

/* Modal 樣式 */
.modal-content {
  padding-top: 16px;
}

.modal-feature-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.users-table {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.users-table :deep(.ant-table-thead > tr > th) {
  background: #f3f4f6;
  font-weight: 600;
}

/* 表格樣式 */
:deep(.ant-table-tbody > tr) {
  cursor: pointer;
}

:deep(.ant-table-tbody > tr:hover) {
  background-color: #e0f2fe !important;
}

:deep(.ant-table-tbody > tr:nth-child(even)) {
  background-color: #f9fafb;
}

:deep(.ant-table-expanded-row > td) {
  padding: 0 !important;
  background: #ffffff !important;
}

/* 滾動條樣式 */
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