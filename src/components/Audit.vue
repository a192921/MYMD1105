<!-- Audit.vue -->
<template>
  <div class="content-wrapper">
    <h1 class="page-title">Audit log（審計記錄）</h1>
    
    <a-card title="審計記錄查詢" class="table-card">
      <template #extra>
        <a-space :size="12">
          <!-- Start Date -->
          <a-date-picker
            v-model:value="startDate"
            placeholder="Start date"
            format="YYYY-MM-DD"
            style="width: 140px"
          />

          <!-- 分隔符 -->
          <span style="color: #9ca3af">—</span>

          <!-- End Date -->
          <a-date-picker
            v-model:value="endDate"
            placeholder="End date"
            format="YYYY-MM-DD"
            style="width: 140px"
          >
            <template #suffixIcon>
              <CalendarOutlined />
            </template>
          </a-date-picker>

          <!-- Action 篩選 -->
          <a-select
            v-model:value="actionFilter"
            mode="multiple"
            placeholder="Action= upload/ login/ run/delete"
            style="width: 280px"
            :options="actionOptions"
            :max-tag-count="2"
          />

          <!-- 每頁筆數 -->
          <a-select
            v-model:value="pageSize"
            placeholder="每頁筆數"
            style="width: 120px"
            :options="pageSizeOptions"
          />

          <!-- 查詢按鈕 -->
          <a-button 
            type="primary" 
            @click="handleSearch"
            :loading="loading"
          >
            查詢
          </a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data-source="auditData"
        :pagination="paginationConfig"
        :loading="loading"
        :scroll="{ y: 'calc(100vh - 380px)' }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'details'">
            <span :class="{'detail-link': isLink(record.details)}">
              {{ record.details }}
            </span>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { CalendarOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import dayjs from 'dayjs';
import { api } from '../utils/api';

const loading = ref(false);
const startDate = ref(null);
const endDate = ref(null);
const actionFilter = ref([]);
const pageSize = ref(20);
const currentPage = ref(1);
const totalRecords = ref(0);

const actionOptions = [
  { label: 'upload', value: 'upload' },
  { label: 'login', value: 'login' },
  { label: 'run', value: 'run' },
  { label: 'delete', value: 'delete' }
];

const pageSizeOptions = [
  { label: '20 筆/頁', value: 20 },
  { label: '50 筆/頁', value: 50 },
  { label: '100 筆/頁', value: 100 },
  { label: '200 筆/頁', value: 200 }
];

const columns = [
  { 
    title: 'log_id', 
    dataIndex: 'logId', 
    key: 'logId',
    width: 120
  },
  { 
    title: 'customer_ID', 
    dataIndex: 'customerId', 
    key: 'customerId',
    width: 150
  },
  { 
    title: 'action', 
    dataIndex: 'action', 
    key: 'action',
    width: 120
  },
  { 
    title: 'details', 
    dataIndex: 'details', 
    key: 'details',
    width: 180
  },
  { 
    title: 'timestamp', 
    dataIndex: 'timestamp', 
    key: 'timestamp',
    width: 200
  }
];

const auditData = ref([]);

// 分頁配置
const paginationConfig = computed(() => ({
  current: currentPage.value,
  pageSize: pageSize.value,
  total: totalRecords.value,
  showSizeChanger: false,
  showTotal: (total) => `共 ${total} 筆記錄`,
  showQuickJumper: true,
}));

// API 請求函數
const fetchAuditLogs = async () => {
  loading.value = true;
  
  try {
    // 構建 API 參數
    const params = {
      page: currentPage.value,
      size: pageSize.value
    };

    // 添加日期參數
    if (startDate.value) {
      params.startDate = dayjs(startDate.value).format('YYYY-MM-DD');
    }
    if (endDate.value) {
      params.endDate = dayjs(endDate.value).format('YYYY-MM-DD');
    }

    // 添加 action 篩選參數（如果 API 支援）
    if (actionFilter.value && actionFilter.value.length > 0) {
      params.actions = actionFilter.value.join(',');
    }

    // 使用 api 工具發送請求
    const response = await api.get('/api/audit-logs', { params });

    console.log('審計記錄 API 回應:', response.data);

    // 處理不同的回應格式
    let logs = [];
    let total = 0;

    if (response.data && response.data.res && Array.isArray(response.data.res.data)) {
      logs = response.data.res.data;
      total = response.data.res.total || response.data.res.pagination?.total || logs.length;
    } else if (response.data && Array.isArray(response.data.data)) {
      logs = response.data.data;
      total = response.data.total || response.data.pagination?.total || logs.length;
    } else if (Array.isArray(response.data)) {
      logs = response.data;
      total = logs.length;
    }

    // 映射資料
    auditData.value = logs.map((item, index) => ({
      key: `${currentPage.value}-${index}`,
      logId: item.log_id || item.logId || item.id,
      customerId: item.customer_id || item.customerId || item.userId,
      action: item.action,
      details: item.details || item.detail,
      timestamp: item.timestamp || item.created_at || item.createdAt
    }));

    totalRecords.value = total;

    message.success('審計記錄載入成功');

  } catch (error) {
    console.error('獲取審計記錄失敗:', error);
    message.error('獲取審計記錄失敗，請稍後再試');
    
    // 使用假資料作為後備
    auditData.value = [
      { key: '1', logId: '00000110', customerId: 'NVT00120', action: 'login', details: 'login2022', timestamp: '20220102 09:20:30' },
      { key: '2', logId: '00000104', customerId: 'NVT00134', action: 'upload', details: 'upload', timestamp: '20220102 09:20:30' },
      { key: '3', logId: '00003134', customerId: 'NVT03134', action: 'run', details: 'Run_01', timestamp: '20211102 09:20:30' },
      { key: '4', logId: '00000220', customerId: 'NVT00220', action: 'delete', details: 'delete2', timestamp: '20230102 09:20:30' },
      { key: '5', logId: '00000334', customerId: 'NVT03334', action: 'delete', details: 'delete', timestamp: '20240102 09:20:30' },
      { key: '6', logId: '00003131', customerId: 'NVT03131', action: 'delete', details: 'delete', timestamp: '20250102 09:20:30' },
      { key: '7', logId: '000023221', customerId: 'NVT023221', action: 'run', details: 'Run_22', timestamp: '20250102 09:20:30' },
      { key: '8', logId: '00002131', customerId: 'NVT02131', action: 'run', details: 'Run_233', timestamp: '20120102 09:20:22' },
      { key: '9', logId: '000002331', customerId: 'NVT02331', action: 'run', details: 'run', timestamp: '20210102 10:20:50' },
      { key: '10', logId: '000013221', customerId: 'NVT013221', action: 'upload', details: 'upload', timestamp: '20220102 00:20:34' }
    ];
    totalRecords.value = 100;
  } finally {
    loading.value = false;
  }
};

// 處理查詢按鈕點擊
const handleSearch = () => {
  // 驗證日期範圍
  if (startDate.value && endDate.value) {
    if (dayjs(startDate.value).isAfter(dayjs(endDate.value))) {
      message.warning('開始日期不能晚於結束日期');
      return;
    }
  }

  currentPage.value = 1; // 重置到第一頁
  fetchAuditLogs();
};

// 處理表格變更（分頁、排序等）
const handleTableChange = (pagination) => {
  currentPage.value = pagination.current;
  fetchAuditLogs();
};

// 判斷是否為連結
const isLink = (details) => {
  return details && (details.includes('Upload_image') || details.includes('Upload'));
};

// 初始載入資料
onMounted(() => {
  fetchAuditLogs();
});
</script>

<style scoped>
.content-wrapper {
  padding: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 32px;
}

.table-card :deep(.ant-card-head-title) {
  font-size: 18px;
  font-weight: 600;
}

.table-card :deep(.ant-card-extra) {
  display: flex;
  align-items: center;
}

/* 讓 details 欄位中的連結顯示為紅色底線 */
.detail-link {
  color: #ef4444;
  text-decoration: underline;
  text-decoration-style: wavy;
  cursor: pointer;
}

/* 表格斑馬紋 */
:deep(.ant-table-tbody > tr:nth-child(even)) {
  background-color: #f9fafb;
}

:deep(.ant-table-tbody > tr:hover) {
  background-color: #f3f4f6 !important;
}

/* 自定義滾動條 */
:deep(.ant-table-body)::-webkit-scrollbar {
  width: 8px;
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

/* 響應式設計 */
@media (max-width: 1200px) {
  .table-card :deep(.ant-card-extra) {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>