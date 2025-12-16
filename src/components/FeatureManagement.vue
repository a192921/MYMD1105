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
          <a-table
            :columns="authorizedUserColumns"
            :data-source="feature.users"
            :loading="feature.usersLoading"
            size="small"
            :pagination="false"
          >
            <template #bodyCell="{ column, record: user }">
              <template v-if="column.key === 'status'">
                <a-switch
                  checked
                  checked-children="已授權"
                  un-checked-children="移除"
                  @change="() => revokeUser(feature, user)"
                />
              </template>
            </template>
          </a-table>
        </template>
      </a-table>
    </a-card>

    <!-- 授權使用者 Modal -->
    <a-modal
      v-model:open="userModalVisible"
      title="授權使用者"
      width="900px"
      @cancel="userModalVisible = false"
    >
      <a-table
        :columns="allUserColumns"
        :data-source="mappedUsers"
        :pagination="false"
      >
        <template #bodyCell="{ column, record: user }">
          <template v-if="column.key === 'status'">
            <a-switch
              :checked="user.authorized"
              checked-children="已授權"
              un-checked-children="未授權"
              @change="(checked) => toggleAuthorize(checked, user)"
            />
          </template>
        </template>
      </a-table>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { api } from '../utils/api';

/* ================= 狀態 ================= */
const featureData = ref([]);
const allUsers = ref([]);
const expandedRowKeys = ref([]);
const tableLoading = ref(false);
const userModalVisible = ref(false);
const currentFeature = ref(null);

/* ================= 欄位 ================= */
const featureColumns = [
  { title: '功能名稱', dataIndex: 'featureName', key: 'featureName' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '', key: 'action', width: 150 }
];

const authorizedUserColumns = [
  { title: 'Username', dataIndex: 'username', key: 'username' },
  { title: 'Email', dataIndex: 'email', key: 'email' },
  { title: '狀態', key: 'status', width: 120 }
];

const allUserColumns = authorizedUserColumns;

/* ================= 計算：授權狀態 ================= */
const mappedUsers = computed(() => {
  if (!currentFeature.value) return [];
  const authorizedIds = currentFeature.value.users.map(u => u.key);
  return allUsers.value.map(u => ({
    ...u,
    authorized: authorizedIds.includes(u.key)
  }));
});

/* ================= API ================= */
const fetchFeatures = async () => {
  tableLoading.value = true;
  try {
    const res = await api.get('/features');
    featureData.value = res.data.data.map(f => ({
      key: f.id.toString(),
      featureName: f.featureName,
      description: f.description,
      users: [],
      usersLoading: false
    }));
  } catch (e) {
    // 假資料（Feature）
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

const fetchFeatureUsers = async (feature) => {
  feature.usersLoading = true;
  try {
    const res = await api.get(`/features/${feature.key}/customers`);
    feature.users = res.data.data.map(u => ({
      key: u.id.toString(),
      username: u.username,
      email: u.email
    }));
  } catch (e) {
    // 假資料（Feature Users）
    feature.users = feature.key === '1'
      ? [
          { key: '101', username: 'Amy', email: 'amy@test.com' },
          { key: '102', username: 'Eric', email: 'eric@test.com' }
        ]
      : [
          { key: '103', username: 'Hailey', email: 'hailey@test.com' }
        ];
  } finally {
    feature.usersLoading = false;
  }
};

const fetchAllUsers = async () => {
  try {
    const res = await api.get('/users/all');
    allUsers.value = res.data.data.map(u => ({
      key: u.id.toString(),
      username: u.username,
      email: u.email
    }));
  } catch (e) {
    // 假資料（All Users）
    allUsers.value = [
      { key: '101', username: 'Amy', email: 'amy@test.com' },
      { key: '102', username: 'Eric', email: 'eric@test.com' },
      { key: '103', username: 'Hailey', email: 'hailey@test.com' },
      { key: '104', username: 'Angela', email: 'angela@test.com' }
    ];
  }
};

/* ================= 事件 ================= */
const handleExpand = async (expanded, feature) => {
  if (expanded) {
    expandedRowKeys.value = [feature.key];
    await fetchFeatureUsers(feature);
  } else {
    expandedRowKeys.value = [];
  }
};

const openUserModal = (feature) => {
  currentFeature.value = feature;
  userModalVisible.value = true;
};

const toggleAuthorize = async (checked, user) => {
  const fid = currentFeature.value.key;
  try {
    if (checked) {
      await api.post(`/features/${fid}/customers/${user.key}`);
      message.success(`已授權 ${user.username}`);
    } else {
      await api.delete(`/features/${fid}/customers/${user.key}`);
      message.success(`已取消 ${user.username}`);
    }
    await fetchFeatureUsers(currentFeature.value);
  } catch {
    message.error('更新授權失敗');
  }
};

const revokeUser = async (feature, user) => {
  await api.delete(`/features/${feature.key}/customers/${user.key}`);
  await fetchFeatureUsers(feature);
};

onMounted(() => {
  fetchFeatures();
  fetchAllUsers();
});
</script>

<style scoped>
.content-wrapper { padding: 32px; }
.page-title { font-size: 24px; margin-bottom: 16px; }
</style>
