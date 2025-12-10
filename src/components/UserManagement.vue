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

    // 根據你的 API 格式：{ res: { status: true, data: [...] } }
    console.log('API 回應:', response);
    
    let users = [];
    
    // 檢查你的 API 格式
    if (response.data && response.data.res && Array.isArray(response.data.res.data)) {
      // 格式: { data: { res: { data: [...] } } }
      users = response.data.res.data;
      console.log('✓ 使用格式: response.data.res.data');
    } else if (response.res && Array.isArray(response.res.data)) {
      // 格式: { res: { data: [...] } }
      users = response.res.data;
      console.log('✓ 使用格式: response.res.data');
    } else if (response.data && Array.isArray(response.data.data)) {
      // 備用格式: { data: { data: [...] } }
      users = response.data.data;
      console.log('✓ 使用格式: response.data.data');
    } else if (Array.isArray(response.data)) {
      // 備用格式: { data: [...] }
      users = response.data;
      console.log('✓ 使用格式: response.data');
    } else {
      console.error('❌ 無法解析 API 回應格式:', response);
      throw new Error('API 回應格式不正確');
    }

    console.log('解析後的使用者資料:', users);
    console.log('使用者數量:', users.length);

    // 檢查是否成功取得資料
    if (!Array.isArray(users) || users.length === 0) {
      console.warn('⚠️ 沒有取得任何使用者資料');
      userData.value = [];
      paginationConfig.value.total = 0;
      message.warning('目前沒有使用者資料');
      return;
    }

    // 顯示第一筆資料
    if (users.length > 0) {
      console.log('第一筆使用者:', users[0]);
    }

    // 映射資料到表格格式
    // API 欄位: userId, email, displayName
    userData.value = users.map((user, index) => ({
      key: user.userId || index.toString(),
      customerId: user.userId,      // userId → customer_ID
      username: user.displayName,   // displayName → Username
      email: user.email,            // email → email
    }));

    console.log('映射後的表格資料:', userData.value);

    // 更新分頁資訊
    const total = response.data?.res?.total || 
                  response.res?.total || 
                  response.data?.total || 
                  users.length;
    paginationConfig.value.total = total;

    message.success(`成功載入 ${userData.value.length} 筆使用者資料`);
  } catch (error) {
    console.error('取得使用者列表失敗:', error);
    message.error('載入使用者列表失敗');

    // 使用假資料作為備用（符合你的 API 格式）
    userData.value = [
      { key: 'Queena_Wu', customerId: 'Queena_Wu', username: 'Queena', email: 'Queena@gmail.com' },
      { key: 'John_Doe', customerId: 'John_Doe', username: 'John', email: 'John@gmail.com' },
      { key: 'Amy_Chen', customerId: 'Amy_Chen', username: 'Amy', email: 'Amy@gmail.com' },
      { key: 'Eric_Lin', customerId: 'Eric_Lin', username: 'Eric', email: 'Eric@gmail.com' },
      { key: 'Anna_Wang', customerId: 'Anna_Wang', username: 'Anna', email: 'Anna@gmail.com' },
    ];
    paginationConfig.value.total = 5;
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