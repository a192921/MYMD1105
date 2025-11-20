<!-- JobManagement.vue -->
<template>
  <div class="content-wrapper">
    <h1 class="page-title">Job監控</h1>
    
    <a-card title="Job 執行狀態" class="table-card">
      <template #extra>
        <div class="filter-container">
          <!-- Start Date -->
          <a-date-picker
            v-model:value="startDate"
            placeholder="Start date"
            format="YYYY-MM-DD"
            style="width: 130px"
          />

          <!-- 分隔符 -->
          <span class="separator">—</span>

          <!-- End Date -->
          <a-date-picker
            v-model:value="endDate"
            placeholder="End date"
            format="YYYY-MM-DD"
            style="width: 130px"
          >
            <template #suffixIcon>
              <CalendarOutlined />
            </template>
          </a-date-picker>

          <!-- Status 篩選 -->
          <a-select
            v-model:value="statusFilter"
            mode="multiple"
            placeholder="Status= Pending/Running/ Done/Failed"
            style="width: 280px"
            :options="statusOptions"
            :max-tag-count="2"
          />

          <!-- 查詢按鈕 -->
          <a-button 
            type="primary" 
            @click="handleSearch"
            size="middle"
          >
            查詢
          </a-button>
        </div>
      </template>

      <a-table
        :columns="columns"
        :data-source="filteredData"
        :pagination="false"
        :loading="loading"
        :scroll="{ y: 'calc(100vh - 320px)' }"
        :expandedRowKeys="expandedRowKeys"
        @expand="handleExpand"
        :expandRowByClick="true"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ record.status }}
            </a-tag>
          </template>
        </template>

        <!-- 展開的內容 - 顯示 JobFile 列表 -->
        <template #expandedRowRender="{ record }">
          <div class="expanded-content">
            <!-- JobFile 列表 -->
            <div class="job-files-section">
              <h4 class="section-title">
                <FileTextOutlined style="margin-right: 8px" />
                Job Files ({{ record.jobFiles.length }})
              </h4>
              
              <a-table
                :columns="fileColumns"
                :data-source="record.jobFiles"
                :pagination="false"
                size="small"
                :scroll="{ y: 300 }"
                class="files-table"
              >
                <template #bodyCell="{ column, record: file }">
                  <template v-if="column.key === 'fileSize'">
                    {{ formatFileSize(file.fileSize) }}
                  </template>
                  <template v-if="column.key === 'action'">
                    <a-space>
                      <a-button type="link" size="small" @click="handleRetry(file)">
                        <ReloadOutlined /> 重試
                      </a-button>
                      <a-button type="link" size="small" @click="handleCancel(file)">
                        <StopOutlined /> 取消
                      </a-button>
                      <a-button type="link" danger size="small" @click="handleDelete(file)">
                        <DeleteOutlined /> 刪除
                      </a-button>
                    </a-space>
                  </template>
                </template>
              </a-table>
            </div>
          </div>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { 
  CalendarOutlined, 
  FileTextOutlined,
  ReloadOutlined,
  StopOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
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

// 主表格欄位
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

// JobFile 表格欄位
const fileColumns = [
  { 
    title: 'File ID', 
    dataIndex: 'fileId', 
    key: 'fileId',
    width: 100
  },
  { 
    title: 'File Name', 
    dataIndex: 'fileName', 
    key: 'fileName',
    width: 250
  },
  { 
    title: 'File Type', 
    dataIndex: 'fileType', 
    key: 'fileType',
    width: 100
  },
  { 
    title: 'File Size', 
    dataIndex: 'fileSize', 
    key: 'fileSize',
    width: 100
  },
  { 
    title: 'Upload Time', 
    dataIndex: 'uploadTime', 
    key: 'uploadTime',
    width: 180
  },
  { 
    title: '操作', 
    key: 'action',
    width: 200,
    fixed: 'right'
  }
];

// Job 資料（含 JobFile）
const jobData = ref([
  { 
    key: '1', 
    jobId: '00000110', 
    customerId: 'NVT00120', 
    status: 'Running', 
    timestamp: '20220102 09:20:30',
    featureId: '',
    createdAt: '20220102 09:20:30',
    completedAt: '20220103 09:20:20',
    jobFiles: [
      { key: 'f1', fileId: 'F001', fileName: 'input_data.csv', fileType: 'CSV', fileSize: 2048576, uploadTime: '20220102 09:15:20' },
      { key: 'f2', fileId: 'F002', fileName: 'config.json', fileType: 'JSON', fileSize: 4096, uploadTime: '20220102 09:16:30' },
      { key: 'f3', fileId: 'F003', fileName: 'result_output.xlsx', fileType: 'XLSX', fileSize: 5242880, uploadTime: '20220102 09:20:30' }
    ]
  },
  { 
    key: '2', 
    jobId: '00000104', 
    customerId: 'NVT00134', 
    status: 'Done', 
    timestamp: '20220102 09:20:30',
    featureId: 'FT001',
    createdAt: '20220102 09:20:30',
    completedAt: '20220102 10:30:45',
    jobFiles: [
      { key: 'f4', fileId: 'F004', fileName: 'dataset.csv', fileType: 'CSV', fileSize: 10485760, uploadTime: '20220102 09:18:00' },
      { key: 'f5', fileId: 'F005', fileName: 'report.pdf', fileType: 'PDF', fileSize: 1048576, uploadTime: '20220102 10:30:45' }
    ]
  },
  { 
    key: '3', 
    jobId: '00003134', 
    customerId: 'NVT03134', 
    status: 'Running', 
    timestamp: '20211102 09:20:30',
    featureId: 'FT002',
    createdAt: '20211102 09:20:30',
    completedAt: null,
    jobFiles: [
      { key: 'f6', fileId: 'F006', fileName: 'image_001.png', fileType: 'PNG', fileSize: 524288, uploadTime: '20211102 09:19:00' },
      { key: 'f7', fileId: 'F007', fileName: 'image_002.png', fileType: 'PNG', fileSize: 614400, uploadTime: '20211102 09:19:30' },
      { key: 'f8', fileId: 'F008', fileName: 'image_003.png', fileType: 'PNG', fileSize: 458752, uploadTime: '20211102 09:20:00' },
      { key: 'f9', fileId: 'F009', fileName: 'metadata.xml', fileType: 'XML', fileSize: 8192, uploadTime: '20211102 09:20:30' }
    ]
  },
  { 
    key: '4', 
    jobId: '00000220', 
    customerId: 'NVT00220', 
    status: 'Failed', 
    timestamp: '20230102 09:20:30',
    featureId: '',
    createdAt: '20230102 09:20:30',
    completedAt: '20230102 09:25:15',
    jobFiles: [
      { key: 'f10', fileId: 'F010', fileName: 'error_log.txt', fileType: 'TXT', fileSize: 2048, uploadTime: '20230102 09:25:15' }
    ]
  },
  { 
    key: '5', 
    jobId: '00000334', 
    customerId: 'NVT03334', 
    status: 'Failed', 
    timestamp: '20240102 09:20:30',
    featureId: 'FT003',
    createdAt: '20240102 09:20:30',
    completedAt: null,
    jobFiles: []
  },
  { 
    key: '6', 
    jobId: '00003131', 
    customerId: 'NVT03131', 
    status: 'Failed', 
    timestamp: '20250102 09:20:30',
    featureId: '',
    createdAt: '20250102 09:20:30',
    completedAt: null,
    jobFiles: [
      { key: 'f11', fileId: 'F011', fileName: 'backup.zip', fileType: 'ZIP', fileSize: 20971520, uploadTime: '20250102 09:20:00' }
    ]
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

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
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

const handleRetry = (file) => {
  message.loading(`正在重試處理檔案: ${file.fileName}...`, 1);
  setTimeout(() => {
    message.success(`檔案重試成功: ${file.fileName}`);
  }, 1000);
  // 實際重試邏輯
};

const handleCancel = (file) => {
  Modal.confirm({
    title: '確認取消',
    content: `確定要取消處理檔案「${file.fileName}」嗎？`,
    okText: '確定',
    cancelText: '取消',
    onOk() {
      message.success(`已取消處理: ${file.fileName}`);
      // 實際取消邏輯
    }
  });
};

const handleDelete = (file) => {
  Modal.confirm({
    title: '確認刪除',
    content: `確定要刪除檔案「${file.fileName}」嗎？此操作無法復原。`,
    okText: '確定刪除',
    cancelText: '取消',
    okType: 'danger',
    onOk() {
      message.success(`已刪除檔案: ${file.fileName}`);
      // 實際刪除邏輯
    }
  });
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

.table-card :deep(.ant-card-extra) {
  display: flex;
  align-items: center;
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.separator {
  color: #9ca3af;
  font-size: 16px;
  margin: 0 4px;
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
  margin: 0;
}

/* JobFile 區塊 */
.job-files-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.files-table {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.files-table :deep(.ant-table-thead > tr > th) {
  background: #f3f4f6;
  font-weight: 600;
}

.files-table :deep(.ant-table-tbody > tr:hover) {
  background-color: #f0f9ff !important;
}

/* 表格斑馬紋 */
:deep(.ant-table-tbody > tr:nth-child(even)) {
  background-color: #f9fafb;
}

/* 展開行的背景 */
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

/* 響應式設計 */
@media (max-width: 1200px) {
  .filter-container {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>