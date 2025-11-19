<!-- JobManagement.vue -->
<template>
  <div class="page-wrapper">
    <!-- 頂部工具列 -->
    <div class="top-bar">
      <div class="top-bar-left">
        <h1 class="page-title">Job監控</h1>
      </div>
    </div>

    <div class="content-wrapper">
      <a-card class="filter-card">
        <a-row :gutter="16" align="middle">
          <!-- Start Date -->
          <a-col :xs="24" :sm="8" :md="6">
            <a-date-picker
              v-model:value="startDate"
              placeholder="Start date"
              style="width: 100%"
              format="YYYY-MM-DD"
            />
          </a-col>

          <!-- 分隔符 -->
          <a-col :xs="24" :sm="2" :md="1" class="separator">
            <span>—</span>
          </a-col>

          <!-- End Date -->
          <a-col :xs="24" :sm="8" :md="6">
            <a-date-picker
              v-model:value="endDate"
              placeholder="End date"
              style="width: 100%"
              format="YYYY-MM-DD"
            >
              <template #suffixIcon>
                <CalendarOutlined />
              </template>
            </a-date-picker>
          </a-col>

          <!-- Status 篩選 -->
          <a-col :xs="24" :sm="12" :md="8">
            <a-select
              v-model:value="statusFilter"
              mode="multiple"
              placeholder="Status= Pending/Running/ Done/Failed"
              style="width: 100%"
              :options="statusOptions"
              :max-tag-count="2"
            />
          </a-col>

          <!-- 查詢按鈕 -->
          <a-col :xs="24" :sm="12" :md="3">
            <a-button 
              type="primary" 
              @click="handleSearch"
              block
              size="large"
            >
              查詢
            </a-button>
          </a-col>
        </a-row>
      </a-card>

      <!-- 表格 -->
      <a-card class="table-card">
        <a-table
          :columns="columns"
          :data-source="filteredData"
          :pagination="false"
          :loading="loading"
          :scroll="{ y: 'calc(100vh - 200px)' }"
          :expandedRowKeys="expandedRowKeys"
          @expand="handleExpand"
          :expandRowByClick="true"
        >
          <!-- More 欄位 -->
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'status'">
              <a-tag :color="getStatusColor(record.status)">
                {{ record.status }}
              </a-tag>
            </template>
          </template>

          <!-- 展開的內容 -->
          <template #expandedRowRender="{ record }">
            <div class="expanded-content">
              <a-row :gutter="[16, 16]">
                <a-col :span="24">
                  <div class="detail-item">
                    <span class="detail-label">Job_id:</span>
                    <span class="detail-value">{{ record.jobId }}</span>
                  </div>
                </a-col>
                <a-col :span="24">
                  <div class="detail-item">
                    <span class="detail-label">customer_id:</span>
                    <span class="detail-value">{{ record.customerId }}</span>
                  </div>
                </a-col>
                <a-col :span="24">
                  <div class="detail-item">
                    <span class="detail-label">Feature_Id:</span>
                    <span class="detail-value">{{ record.featureId || '-' }}</span>
                  </div>
                </a-col>
                <a-col :span="24">
                  <div class="detail-item">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value">
                      <a-tag :color="getStatusColor(record.status)">
                        {{ record.status }}
                      </a-tag>
                    </span>
                  </div>
                </a-col>
                <a-col :span="24">
                  <div class="detail-item">
                    <span class="detail-label">建立時間:</span>
                    <span class="detail-value">{{ record.createdAt }}</span>
                  </div>
                </a-col>
                <a-col :span="24">
                  <div class="detail-item">
                    <span class="detail-label">完成時間:</span>
                    <span class="detail-value">{{ record.completedAt || '-' }}</span>
                  </div>
                </a-col>
              </a-row>
            </div>
          </template>
        </a-table>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { CalendarOutlined } from '@ant-design/icons-vue';
import dayjs from 'dayjs';

const loading = ref(false);
const startDate = ref(null);
const endDate = ref(null);
const statusFilter = ref([]);
const expandedRowKeys = ref([]);

const statusOptions = [
  { label: 'Pending', value: 'Pending' },
  { label: 'Running', value: 'Running' },
  { label: 'Done', value: 'Done' },
  { label: 'Failed', value: 'Failed' }
];

const columns = [
  { 
    title: 'Job_id', 
    dataIndex: 'jobId', 
    key: 'jobId',
    width: 120
  },
  { 
    title: 'customer_ID', 
    dataIndex: 'customerId', 
    key: 'customerId',
    width: 150
  },
  { 
    title: 'Status', 
    dataIndex: 'status', 
    key: 'status',
    width: 120
  },
  { 
    title: 'timestamp', 
    dataIndex: 'timestamp', 
    key: 'timestamp',
    width: 200
  }
];

const jobData = ref([
  { 
    key: '1', 
    jobId: '00000110', 
    customerId: 'NVT00120', 
    status: 'Running', 
    timestamp: '20220102 09:20:30',
    featureId: '',
    createdAt: '20220102 09:20:30',
    completedAt: '20220103 09:20:20'
  },
  { 
    key: '2', 
    jobId: '00000104', 
    customerId: 'NVT00134', 
    status: 'Done', 
    timestamp: '20220102 09:20:30',
    featureId: 'FT001',
    createdAt: '20220102 09:20:30',
    completedAt: '20220102 10:30:45'
  },
  { 
    key: '3', 
    jobId: '00003134', 
    customerId: 'NVT03134', 
    status: 'Running', 
    timestamp: '20211102 09:20:30',
    featureId: 'FT002',
    createdAt: '20211102 09:20:30',
    completedAt: null
  },
  { 
    key: '4', 
    jobId: '00000220', 
    customerId: 'NVT00220', 
    status: 'Failed', 
    timestamp: '20230102 09:20:30',
    featureId: '',
    createdAt: '20230102 09:20:30',
    completedAt: '20230102 09:25:15'
  },
  { 
    key: '5', 
    jobId: '00000334', 
    customerId: 'NVT03334', 
    status: 'Failed', 
    timestamp: '20240102 09:20:30',
    featureId: 'FT003',
    createdAt: '20240102 09:20:30',
    completedAt: null
  },
  { 
    key: '6', 
    jobId: '00003131', 
    customerId: 'NVT03131', 
    status: 'Failed', 
    timestamp: '20250102 09:20:30',
    featureId: '',
    createdAt: '20250102 09:20:30',
    completedAt: null
  },
  { 
    key: '7', 
    jobId: '000023221', 
    customerId: 'NVT023221', 
    status: 'Running', 
    timestamp: '20250102 09:20:30',
    featureId: 'FT004',
    createdAt: '20250102 09:20:30',
    completedAt: null
  },
  { 
    key: '8', 
    jobId: '00002131', 
    customerId: 'NVT02131', 
    status: 'Running', 
    timestamp: '20120102 09:20:22',
    featureId: '',
    createdAt: '20120102 09:20:22',
    completedAt: null
  },
  { 
    key: '9', 
    jobId: '000002331', 
    customerId: 'NVT02331', 
    status: 'Running', 
    timestamp: '20210102 10:20:50',
    featureId: 'FT005',
    createdAt: '20210102 10:20:50',
    completedAt: null
  },
  { 
    key: '10', 
    jobId: '000013221', 
    customerId: 'NVT013221', 
    status: 'Failed', 
    timestamp: '20220102 00:20:34',
    featureId: '',
    createdAt: '20220102 00:20:34',
    completedAt: '20220102 00:25:10'
  },
  { 
    key: '11', 
    jobId: '000013331', 
    customerId: 'NVT013331', 
    status: 'Running', 
    timestamp: '20220102 09:10:33',
    featureId: 'FT006',
    createdAt: '20220102 09:10:33',
    completedAt: null
  }
]);

const filteredData = computed(() => {
  let result = jobData.value;

  // 日期篩選
  if (startDate.value) {
    const start = dayjs(startDate.value).format('YYYYMMDD');
    result = result.filter(item => {
      const itemDate = item.timestamp.split(' ')[0];
      return itemDate >= start;
    });
  }

  if (endDate.value) {
    const end = dayjs(endDate.value).format('YYYYMMDD');
    result = result.filter(item => {
      const itemDate = item.timestamp.split(' ')[0];
      return itemDate <= end;
    });
  }

  // Status 篩選
  if (statusFilter.value && statusFilter.value.length > 0) {
    result = result.filter(item =>
      statusFilter.value.includes(item.status)
    );
  }

  return result;
});

const getStatusColor = (status) => {
  const colors = {
    'Running': 'blue',
    'Done': 'green',
    'Failed': 'red',
    'Pending': 'orange'
  };
  return colors[status] || 'default';
};

const toggleExpand = (key) => {
  const index = expandedRowKeys.value.indexOf(key);
  if (index > -1) {
    expandedRowKeys.value.splice(index, 1);
  } else {
    expandedRowKeys.value = [key]; // 只展開一個
  }
};

const handleExpand = (expanded, record) => {
  if (expanded) {
    expandedRowKeys.value = [record.key];
  } else {
    expandedRowKeys.value = [];
  }
};

const handleSearch = () => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 500);
};
</script>

<style scoped>
.page-wrapper {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px 0 32px;
  flex-shrink: 0;
}

.top-bar-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
  margin: 0;
}

.content-wrapper {
  flex: 1;
  padding: 24px 32px 32px 32px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filter-card {
  margin-bottom: 24px;
  flex-shrink: 0;
}

.separator {
  text-align: center;
  font-size: 18px;
  color: #9ca3af;
}

.table-card {
  flex: 1;
  overflow: hidden;
}

.table-card :deep(.ant-card-body) {
  height: 100%;
  padding: 0;
}

/* 表格行可點擊提示 */
:deep(.ant-table-tbody > tr) {
  cursor: pointer;
}

:deep(.ant-table-tbody > tr:hover) {
  background-color: #e0f2fe !important;
}

/* 展開內容樣式 */
.expanded-content {
  background: #f9fafb;
  padding: 24px;
  border-left: 3px solid #3b82f6;
  margin: 8px 0;
}

.detail-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.detail-label {
  font-weight: 600;
  color: #374151;
  min-width: 100px;
  margin-right: 16px;
}

.detail-value {
  color: #6b7280;
}

/* 表格斑馬紋 */
:deep(.ant-table-tbody > tr:nth-child(even)) {
  background-color: #f9fafb;
}

:deep(.ant-table-tbody > tr:hover) {
  background-color: #f3f4f6 !important;
}

/* 展開行的背景 */
:deep(.ant-table-expanded-row > td) {
  padding: 0 !important;
  background: #ffffff !important;
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
@media (max-width: 768px) {
  .separator {
    display: none;
  }
  
  .content-wrapper {
    padding: 16px;
  }
}
</style>