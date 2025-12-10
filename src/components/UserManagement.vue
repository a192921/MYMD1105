<template>
  <div class="page-container">
    <h1 class="page-title">使用者管理</h1>
    
    <a-card title="使用者權限" class="table-card">
      <template #extra>
        <a-space>
          <a-input-search
            v-model:value="searchText"
            placeholder="Username"
            style="width: 250px"
            @search="handleSearch"
            :loading="loading"
          >
            <template #prefix>
              <SearchOutlined />
            </template>
          </a-input-search>
          
          <a-button @click="handleRefresh" :loading="loading">
            <ReloadOutlined /> 重新整理
          </a-button>
        </a-space>
      </template>
      
      <a-table
        :columns="columns"
        :data-source="userData"
        :pagination="paginationConfig"
        :loading="loading"
        :scroll="{ y: 'calc(100vh - 320px)' }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <!-- Email 欄位特殊樣式 -->
          <template v-if="column.key === 'email'">
            <span style="color: #3b82f6">{{ record.email }}</span>
          </template>
          
          <!-- 操作欄（可選） -->
          <!-- <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">
                <EditOutlined /> 編輯
              </a-button>
              <a-button type="link" danger size="small" @click="handleDelete(record)">
                <DeleteOutlined /> 刪除
              </a-button>
            </a-space>
          </template> -->
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { SearchOutlined, ReloadOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { api } from '../utils/api'; // 引入 API 工具

// ============================================
// 狀態管理
// ============================================
const loading = ref(false);
const searchText = ref('');
const userData = ref([]);

// 分頁設定
const paginationConfig = ref({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 筆資料`,
  pageSizeOptions: ['10', '20', '50', '100'],
});

// ============================================
// 表格欄位設定
// ============================================
const columns = [
  { 
    title: 'customer_ID', 
    dataIndex: 'customerId', 
    key: 'customerId',
    width: 150,
    sorter: true,
  },
  { 
    title: 'Username', 
    dataIndex: 'username', 
    key: 'username',
    width: 200,
  },
  { 
    title: 'email', 
    dataIndex: 'email', 
    key: 'email',
    width: 250,
  },
  // 如果需要操作欄，取消註解
  // { 
  //   title: '操作', 
  //   key: 'action',
  //   width: 150,
  //   fixed: 'right'
  // }
];

// ============================================
// API 呼叫函數
// ============================================

// 取得使用者列表
const fetchUsers = async () => {
  loading.value = true;
  try {
    // 建立查詢參數
    const params = {
      page: paginationConfig.value.current,
      pageSize: paginationConfig.value.pageSize,
    };

    // 加入搜尋關鍵字
    if (searchText.value) {
      params.search = searchText.value;
    }

    const response = await api.get('/users', { params });

    // 檢查回應資料結構
    console.log('API 回應:', response.data);

    // 處理不同的 API 回應格式
    let users = [];
    let total = 0;

    if (response.data) {
      // 格式 1: { data: { users: [...], total: 100 } }
      if (response.data.data && response.data.data.users) {
        users = response.data.data.users;
        total = response.data.data.total || users.length;
      }
      // 格式 2: { data: { items: [...], total: 100 } }
      else if (response.data.data && response.data.data.items) {
        users = response.data.data.items;
        total = response.data.data.total || users.length;
      }
      // 格式 3: { data: [...] }
      else if (Array.isArray(response.data.data)) {
        users = response.data.data;
        total = users.length;
      }
      // 格式 4: { users: [...], total: 100 }
      else if (response.data.users) {
        users = response.data.users;
        total = response.data.total || users.length;
      }
      // 格式 5: 直接是陣列 [...]
      else if (Array.isArray(response.data)) {
        users = response.data;
        total = users.length;
      }
    }

    // 映射資料
    userData.value = users.map((user, index) => ({
      key: user.id?.toString() || user.key?.toString() || index.toString(),
      customerId: user.customerId || user.customer_id || user.customerId || '-',
      username: user.username || user.name || user.userName || '-',
      email: user.email || user.emailAddress || user.mail || '-',
    }));

    // 更新分頁資訊
    paginationConfig.value.total = total;

    message.success(`載入 ${userData.value.length} 筆使用者資料`);
  } catch (error) {
    console.error('取得使用者列表失敗:', error);
    message.error('載入使用者列表失敗');

    // 使用假資料作為備用
    userData.value = [
      { key: '1', customerId: 'NVT00120', username: 'Amy', email: 'Amy@example.com' },
      { key: '2', customerId: 'NVT00134', username: 'anna', email: 'anna@example.com' },
      { key: '3', customerId: 'NVT03134', username: 'Hailey', email: 'Hailey@example.com' },
      { key: '4', customerId: 'NVT00220', username: 'Eric', email: 'Eric@example.com' },
      { key: '5', customerId: 'NVT03334', username: 'Hazel', email: 'Hazel@example.com' },
      { key: '6', customerId: 'NVT03131', username: 'Er', email: 'Er@example.com' },
      { key: '7', customerId: 'NVT023221', username: 'NY', email: 'NY@example.com' },
      { key: '8', customerId: 'NVT02131', username: 'Angela', email: 'Angela@example.com' },
      { key: '9', customerId: 'NVT00121', username: 'Alice', email: 'Alice@example.com' },
      { key: '10', customerId: 'NVT00135', username: 'Nike', email: 'Nike@example.com' },
      { key: '11', customerId: 'NVT03135', username: 'Kiki', email: 'Kiki@example.com' },
      { key: '12', customerId: 'NVT00221', username: 'KC', email: 'KC@example.com' },
      { key: '13', customerId: 'NVT03335', username: 'Eva', email: 'Eva@example.com' },
    ];
    paginationConfig.value.total = 13;
  } finally {
    loading.value = false;
  }
};

// 刪除使用者
const deleteUser = async (userId) => {
  try {
    await api.delete(`/users/${userId}`);
    message.success('使用者刪除成功');
    
    // 重新載入列表
    await fetchUsers();
  } catch (error) {
    console.error('刪除使用者失敗:', error);
    message.error('刪除使用者失敗');
  }
};

// 更新使用者
const updateUser = async (userId, userData) => {
  try {
    await api.put(`/users/${userId}`, userData);
    message.success('使用者更新成功');
    
    // 重新載入列表
    await fetchUsers();
  } catch (error) {
    console.error('更新使用者失敗:', error);
    message.error('更新使用者失敗');
  }
};

// ============================================
// 事件處理函數
// ============================================

// 搜尋按鈕
const handleSearch = async () => {
  paginationConfig.value.current = 1; // 重置到第一頁
  await fetchUsers();
};

// 重新整理按鈕
const handleRefresh = async () => {
  searchText.value = ''; // 清空搜尋
  paginationConfig.value.current = 1;
  await fetchUsers();
};

// 表格分頁/排序變更
const handleTableChange = (pagination, filters, sorter) => {
  paginationConfig.value.current = pagination.current;
  paginationConfig.value.pageSize = pagination.pageSize;
  
  // 如果需要處理排序
  // const sortField = sorter.field;
  // const sortOrder = sorter.order;
  
  fetchUsers();
};

// 編輯使用者
const handleEdit = (user) => {
  Modal.info({
    title: '編輯使用者',
    content: `編輯功能開發中 - 使用者: ${user.username}`,
  });
  // 實際實作：顯示編輯 Modal 或跳轉到編輯頁面
};

// 刪除使用者
const handleDelete = (user) => {
  Modal.confirm({
    title: '確認刪除',
    content: `確定要刪除使用者「${user.username}」(${user.email})嗎？此操作無法復原。`,
    okText: '確定刪除',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      await deleteUser(user.key);
    }
  });
};

// ============================================
// 生命週期
// ============================================

onMounted(async () => {
  // 頁面載入時取得資料
  await fetchUsers();
});
</script>

<style scoped>
.page-container {
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

.table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-card :deep(.ant-card-head) {
  flex-shrink: 0;
}

.table-card :deep(.ant-card-head-title) {
  font-size: 18px;
  font-weight: 600;
}

.table-card :deep(.ant-card-body) {
  flex: 1;
  overflow: hidden;
  padding: 0;
}

/* 表格樣式 */
:deep(.ant-table-tbody > tr:hover) {
  background-color: #e0f2fe !important;
}

:deep(.ant-table-tbody > tr:nth-child(even)) {
  background-color: #f9fafb;
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