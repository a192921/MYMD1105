<template>
  <div class="page-container">
    <h1 class="page-title">使用者管理</h1>
    
    <a-card title="使用者權限" class="table-card">
      <template #extra>
        <a-input-search
          v-model:value="searchText"
          placeholder="Username"
          style="width: 250px"
          @search="handleSearch"
        >
          <template #prefix>
            <SearchOutlined />
          </template>
        </a-input-search>
      </template>

      <a-table
        :columns="columns"
        :data-source="filteredData"
        :pagination="false"
        :loading="loading"
        :scroll="{ y: 'calc(100vh - 320px)' }"
      >
        <!-- <template #bodyCell="{ column }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small">編輯</a-button>
              <a-button type="link" danger size="small">刪除</a-button>
            </a-space>
          </template>
        </template> -->
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { SearchOutlined } from '@ant-design/icons-vue';

const loading = ref(false);
const searchText = ref('');

const columns = [
  { title: 'customer_ID', dataIndex: 'customerId', key: 'customerId' },
  { title: 'Username', dataIndex: 'username', key: 'username' },
  { title: 'email', dataIndex: 'email', key: 'email' }
];

const userData = ref([
  { key: '1', customerId: 1, username: 'Amy', email: 'Amy@example.com' },
  { key: '2', customerId: 2, username: 'anna', email: 'anna@example.com' },
  { key: '3', customerId: 3, username: 'Hailey', email: 'Hailey@example.com' },
  { key: '4', customerId: 4, username: 'Eric', email: 'Eric@example.com' },
  { key: '5', customerId: 5, username: 'Hazel', email: 'Hazel@example.com' },
  { key: '6', customerId: 6, username: 'Er', email: 'Er@example.com' },
  { key: '7', customerId: 7, username: 'NY', email: 'NY@example.com' },
  { key: '8', customerId: 8, username: 'Angela', email: 'Angela@example.com' },
  { key: '9', customerId: 9, username: 'Alice', email: 'Alice@example.com' },
  { key: '10', customerId: 10, username: 'Nike', email: 'Amy@example.com' },
  { key: '11', customerId: 11, username: 'Kiki', email: 'Kiki@example.com' },
  { key: '12', customerId: 12, username: 'KC', email: 'KC@example.com' },
  { key: '13', customerId: 13, username: 'Eva', email: 'Eva@example.com' }
]);

const filteredData = computed(() => {
  if (!searchText.value) return userData.value;
  return userData.value.filter(user =>
    user.username.toLowerCase().includes(searchText.value.toLowerCase())
  );
});

const pagination = {
  pageSize: 20,
  showTotal: (total) => `共 ${total} 筆`
};

const handleSearch = () => {
  // 搜尋功能已在 computed 中實現
};
</script>

<style scoped>
.page-container {
  padding: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 24px;
}

.table-card :deep(.ant-card-head-title) {
  font-size: 18px;
  font-weight: 600;
}
</style>
