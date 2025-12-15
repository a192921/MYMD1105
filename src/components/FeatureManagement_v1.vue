<template>
  <div class="content-wrapper">
    <h1 class="page-title">功能管理</h1>
    
    <div class="action-bar">
      <a-button type="primary" @click="showAddFeatureModal" size="large">
        新增功能
      </a-button>
    </div>

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
          <template v-if="column.key === 'edit'">
            <a-button type="text" @click="handleEdit(record)">
              <EditOutlined style="font-size: 18px" />
            </a-button>
          </template>

          <template v-if="column.key === 'status'">
            <a-switch
              v-model:checked="record.enabled"
              @change="handleStatusChange(record)"
              checked-children="啟用"
              un-checked-children="停用"
            />
          </template>

          <template v-if="column.key === 'action'">
            <a-button type="primary" ghost @click.stop="showAddUserModal(record)">
              新增使用者
            </a-button>
          </template>
        </template>

        <template #expandedRowRender="{ record }">
          <div class="expanded-user-section">
            <h4 class="user-list-title">功能名稱: {{ record.featureName }}</h4>
            <a-table
              :columns="userColumns"
              :data-source="record.users"
              :loading="record.usersLoading"
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
          <a-input v-model:value="featureForm.featureName" />
        </a-form-item>
        <a-form-item label="功能描述" required>
          <a-input v-model:value="featureForm.description" />
        </a-form-item>
        <a-form-item label="啟用/停用" required>
          <a-switch v-model:checked="featureForm.enabled" />
        </a-form-item>
      </a-form>
    </a-modal>

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
          <a-input v-model:value="userSearchText" placeholder="Username" style="width: 250px">
            <template #prefix><SearchOutlined /></template>
          </a-input>
          <a-button type="primary" @click="handleBatchAdd">新增</a-button>
        </div>

        <a-table
          :columns="userColumns"
          :data-source="filteredAvailableUsers"
          :pagination="false"
          :scroll="{ y: 400 }"
          :row-selection="{ selectedRowKeys: selectedUserKeys, onChange: onUserSelectChange }"
        />
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { EditOutlined, SearchOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { api } from '../utils/api';

const featureModalVisible = ref(false);
const userModalVisible = ref(false);
const isEditMode = ref(false);
const currentFeature = ref(null);
const tableLoading = ref(false);
const modalLoading = ref(false);

const featureForm = ref({ featureName: '', description: '', enabled: true });
const userSearchText = ref('');
const selectedUserKeys = ref([]);
const expandedRowKeys = ref([]);

const featureColumns = [
  { title: '', key: 'edit', width: 60, align: 'center' },
  { title: 'Feature_name', dataIndex: 'featureName', key: 'featureName', width: 200 },
  { title: '描述', dataIndex: 'description', key: 'description', width: 200 },
  { title: '啟用', key: 'status', width: 120 },
  { title: '', key: 'action', width: 150 }
];

const userColumns = [
  { title: 'customer_ID', dataIndex: 'customerId', key: 'customerId', width: 150 },
  { title: 'Username', dataIndex: 'username', key: 'username', width: 150 },
  { title: 'email', dataIndex: 'email', key: 'email', width: 200 }
];

const featureData = ref([]);
const allUsers = ref([]);

const filteredAvailableUsers = computed(() => {
  if (!currentFeature.value) return [];
  const existing = currentFeature.value.users.map(u => u.key);
  return allUsers.value.filter(u =>
    !existing.includes(u.key) &&
    (!userSearchText.value || u.username.toLowerCase().includes(userSearchText.value.toLowerCase()))
  );
});

const fetchFeatures = async () => {
  tableLoading.value = true;
  try {
    const res = await api.get('/features');
    featureData.value = res.data.data.map(f => ({
      key: f.id.toString(),
      featureName: f.featureName,
      description: f.description,
      enabled: f.enabled,
      users: [],
      usersLoading: false
    }));
  } catch {
    message.error('載入功能列表失敗');
  } finally {
    tableLoading.value = false;
  }
};

const fetchFeatureUsers = async (feature) => {
  feature.users = [];
  feature.usersLoading = true;
  try {
    const res = await api.get(`/api/admin/features/${feature.key}/customers`);
    feature.users = res.data.data.map(u => ({
      key: u.id.toString(),
      customerId: u.customerId,
      username: u.username,
      email: u.email,
      enabled: u.enabled
    }));
  } catch {
    message.error('載入使用者列表失敗');
  } finally {
    feature.usersLoading = false;
  }
};

const fetchAllUsers = async () => {
  const res = await api.get('/users/all');
  allUsers.value = res.data.data.map(u => ({
    key: u.id.toString(),
    customerId: u.customerId,
    username: u.username,
    email: u.email
  }));
};

onMounted(() => {
  fetchFeatures();
  fetchAllUsers();
});

const handleExpand = async (expanded, record) => {
  if (expanded) {
    expandedRowKeys.value = [record.key];
    await fetchFeatureUsers(record); // 強制 reload
  } else {
    expandedRowKeys.value = [];
  }
};

const showAddFeatureModal = () => {
  isEditMode.value = false;
  featureForm.value = { featureName: '', description: '', enabled: true };
  featureModalVisible.value = true;
};

const handleEdit = (record) => {
  isEditMode.value = true;
  currentFeature.value = record;
  featureForm.value = { ...record };
  featureModalVisible.value = true;
};

const handleFeatureSubmit = async () => {
  featureModalVisible.value = false;
};

const handleFeatureCancel = () => featureModalVisible.value = false;
const handleStatusChange = () => {};

const showAddUserModal = (record) => {
  currentFeature.value = record;
  selectedUserKeys.value = [];
  userModalVisible.value = true;
};

const onUserSelectChange = (keys) => selectedUserKeys.value = keys;
const handleBatchAdd = () => {};
const handleUserSubmit = () => userModalVisible.value = false;
const handleUserCancel = () => userModalVisible.value = false;
</script>

<style scoped>
.content-wrapper { padding: 32px; height: calc(100vh - 64px); display: flex; flex-direction: column; }
.page-title { font-size: 28px; font-weight: bold; margin-bottom: 24px; }
.action-bar { margin-bottom: 24px; }
.table-card { flex: 1; overflow: hidden; }
.expanded-user-section { background: #f9fafb; padding: 24px; }
.user-list-title { margin-bottom: 16px; }
</style>
