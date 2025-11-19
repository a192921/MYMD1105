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

          <!-- 查詢按鈕 -->
          <a-button 
            type="primary" 
            @click="handleSearch"
          >
            查詢
          </a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data-source="filteredData"
        :pagination="false"
        :loading="loading"
        :scroll="{ y: 'calc(100vh - 320px)' }"
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
import { ref, computed } from 'vue';
import { CalendarOutlined } from '@ant-design/icons-vue';
import dayjs from 'dayjs';

const loading = ref(false);
const startDate = ref(null);
const endDate = ref(null);
const actionFilter = ref([]);

const actionOptions = [
  { label: 'upload', value: 'upload' },
  { label: 'login', value: 'login' },
  { label: 'run', value: 'run' },
  { label: 'delete', value: 'delete' }
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

const auditData = ref([
  { key: '1', logId: '00000110', customerId: 'NVT00120', action: 'login', details: 'login2022', timestamp: '20220102 09:20:30' },
  { key: '2', logId: '00000104', customerId: 'NVT00134', action: 'upload', details: 'upload', timestamp: '20220102 09:20:30' },
  { key: '3', logId: '00003134', customerId: 'NVT03134', action: 'run', details: 'Run_01', timestamp: '20211102 09:20:30' },
  { key: '4', logId: '00000220', customerId: 'NVT00220', action: 'delete', details: 'delete2', timestamp: '20230102 09:20:30' },
  { key: '5', logId: '00000334', customerId: 'NVT03334', action: 'delete', details: 'delete', timestamp: '20240102 09:20:30' },
  { key: '6', logId: '00003131', customerId: 'NVT03131', action: 'delete', details: 'delete', timestamp: '20250102 09:20:30' },
  { key: '7', logId: '000023221', customerId: 'NVT023221', action: 'run', details: 'Run_22', timestamp: '20250102 09:20:30' },
  { key: '8', logId: '00002131', customerId: 'NVT02131', action: 'run', details: 'Run_233', timestamp: '20120102 09:20:22' },
  { key: '9', logId: '000002331', customerId: 'NVT02331', action: 'run', details: 'run', timestamp: '20210102 10:20:50' },
  { key: '10', logId: '000013221', customerId: 'NVT013221', action: 'upload', details: 'upload', timestamp: '20220102 00:20:34' },
  { key: '11', logId: '000013331', customerId: 'NVT013331', action: 'run', details: 'run', timestamp: '20220102 09:10:33' },
  { key: '12', logId: '000013221', customerId: 'NVT013221', action: 'login', details: 'login', timestamp: '20220112 09:15:20' },
  { key: '13', logId: '000013223', customerId: 'NVT013223', action: 'login', details: 'login', timestamp: '20221102 09:20:11' },
  { key: '14', logId: '000013224', customerId: 'NVT013224', action: 'upload', details: 'upload', timestamp: '20221102 10:30:11' },
  { key: '15', logId: '000013225', customerId: 'NVT013225', action: 'delete', details: 'delete_file', timestamp: '20221103 11:20:11' },
  { key: '16', logId: '000013226', customerId: 'NVT013226', action: 'run', details: 'Run_44', timestamp: '20221104 09:20:11' },
  { key: '17', logId: '000013227', customerId: 'NVT013227', action: 'login', details: 'login', timestamp: '20221105 09:20:11' },
  { key: '18', logId: '000013228', customerId: 'NVT013228', action: 'upload', details: 'upload', timestamp: '20221106 09:20:11' }
]);

const filteredData = computed(() => {
  let result = auditData.value;

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

  // Action 篩選
  if (actionFilter.value && actionFilter.value.length > 0) {
    result = result.filter(item =>
      actionFilter.value.includes(item.action)
    );
  }

  return result;
});

const isLink = (details) => {
  return details.includes('Upload_image') || details.includes('Upload');
};

const handleSearch = () => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 500);
};
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