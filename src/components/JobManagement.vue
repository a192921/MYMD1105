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
            :loading="loading"
          >
            查詢
          </a-button>

          <!-- 重新整理按鈕 -->
          <a-button 
            @click="handleRefresh"
            size="middle"
            :loading="loading"
          >
            <ReloadOutlined /> 重新整理
          </a-button>
        </div>
      </template>

      <a-table
        :columns="columns"
        :data-source="jobData"
        :pagination="paginationConfig"
        :loading="loading"
        :scroll="{ y: 'calc(100vh - 320px)' }"
        :expandedRowKeys="expandedRowKeys"
        @expand="handleExpand"
        @change="handleTableChange"
        :expandRowByClick="true"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ record.status }}
            </a-tag>
          </template>
          <!-- Job 操作按鈕 -->
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button 
                type="link" 
                size="small" 
                @click.stop="handleJobRetry(record)"
                :disabled="record.status === 'Done'"
              >
                <ReloadOutlined /> 重試
              </a-button>
              <a-button 
                type="link" 
                size="small" 
                @click.stop="handleJobCancel(record)"
                :disabled="record.status !== 'Running' && record.status !== 'Pending'"
              >
                <StopOutlined /> 取消
              </a-button>
              <a-button 
                type="link" 
                danger 
                size="small" 
                @click.stop="handleJobDelete(record)"
              >
                <DeleteOutlined /> 刪除
              </a-button>
            </a-space>
          </template>
        </template>

        <!-- 展開的內容 - 顯示 JobFile 列表 -->
        <template #expandedRowRender="{ record }">
          <div class="expanded-content">
            <!-- JobFile 列表 -->
            <div class="job-files-section">
              <h4 class="section-title">
                <FileTextOutlined style="margin-right: 8px" />
                Job Files ({{ record.jobFiles?.length || 0 }})
              </h4>
              
              <a-table
                :columns="fileColumns"
                :data-source="record.jobFiles || []"
                :pagination="false"
                size="small"
                :scroll="{ y: 300 }"
                :loading="loadingFiles[record.jobId]"
                class="files-table"
              >
                <template #bodyCell="{ column, record: file }">
                  <template v-if="column.key === 'fileSize'">
                    {{ formatFileSize(file.fileSize) }}
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
import { ref, computed, onMounted } from 'vue';
import { 
  CalendarOutlined, 
  FileTextOutlined,
  ReloadOutlined,
  StopOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import dayjs from 'dayjs';
import { api } from '../utils/api'; // 引入 API 工具

// ============================================
// 狀態管理
// ============================================
const loading = ref(false);
const loadingFiles = ref({}); // 用於追蹤個別 Job 的檔案載入狀態
const startDate = ref(null);
const endDate = ref(null);
const statusFilter = ref([]);
const expandedRowKeys = ref([]);
const jobData = ref([]);

// 分頁設定
const paginationConfig = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 筆資料`,
  pageSizeOptions: ['10', '20', '50', '100'],
});

const statusOptions = [
  { label: 'Pending', value: 'Pending' },
  { label: 'Running', value: 'Running' },
  { label: 'Done', value: 'Done' },
  { label: 'Failed', value: 'Failed' }
];

// ============================================
// 表格欄位設定
// ============================================
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
  },
  { 
    title: '操作', 
    key: 'action',
    width: 250,
    fixed: 'right'
  }
];

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
  }
];

// ============================================
// API 呼叫函數
// ============================================

// 取得 Job 列表
const fetchJobs = async () => {
  loading.value = true;
  try {
    // 建立查詢參數
    const params = {
      page: paginationConfig.value.current,
      pageSize: paginationConfig.value.pageSize,
    };

    // 加入日期篩選
    if (startDate.value) {
      params.startDate = dayjs(startDate.value).format('YYYY-MM-DD');
    }
    if (endDate.value) {
      params.endDate = dayjs(endDate.value).format('YYYY-MM-DD');
    }

    // 加入狀態篩選
    if (statusFilter.value && statusFilter.value.length > 0) {
      params.status = statusFilter.value.join(',');
    }

    const response = await api.get('/jobs', { params });

    // 假設 API 回傳格式：
    // {
    //   success: true,
    //   data: {
    //     jobs: [...],
    //     total: 100,
    //     page: 1,
    //     pageSize: 10
    //   }
    // }

    jobData.value = response.data.data.jobs.map(job => ({
      key: job.id.toString(),
      jobId: job.jobId,
      customerId: job.customerId,
      status: job.status,
      timestamp: job.timestamp,
      featureId: job.featureId,
      createdAt: job.createdAt,
      completedAt: job.completedAt,
      jobFiles: [], // 初始為空，展開時才載入
    }));

    // 更新分頁資訊
    paginationConfig.value.total = response.data.data.total;

    message.success('Job 列表載入成功');
  } catch (error) {
    console.error('取得 Job 列表失敗:', error);
    message.error('載入 Job 列表失敗');

    // 使用假資料作為備用
    jobData.value = [
      { 
        key: '1', 
        jobId: '00000110', 
        customerId: 'NVT00120', 
        status: 'Running', 
        timestamp: '20220102 09:20:30',
        featureId: '',
        createdAt: '20220102 09:20:30',
        completedAt: null,
        jobFiles: []
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
        jobFiles: []
      },
    ];
    paginationConfig.value.total = 2;
  } finally {
    loading.value = false;
  }
};

// 取得 Job 的檔案列表（當展開行時呼叫）
const fetchJobFiles = async (jobId) => {
  loadingFiles.value[jobId] = true;
  try {
    const response = await api.get(`/jobs/${jobId}/files`);

    // 假設 API 回傳格式：
    // {
    //   success: true,
    //   data: [
    //     { id: 1, fileId: 'F001', fileName: 'input.csv', ... }
    //   ]
    // }

    const files = response.data.data.map(file => ({
      key: file.id.toString(),
      fileId: file.fileId,
      fileName: file.fileName,
      fileType: file.fileType,
      fileSize: file.fileSize,
      uploadTime: file.uploadTime,
    }));

    // 更新對應 Job 的檔案列表
    const job = jobData.value.find(j => j.jobId === jobId);
    if (job) {
      job.jobFiles = files;
    }

    return files;
  } catch (error) {
    console.error(`取得 Job ${jobId} 的檔案列表失敗:`, error);
    message.error('載入檔案列表失敗');

    // 使用假資料
    const mockFiles = [
      { 
        key: 'f1', 
        fileId: 'F001', 
        fileName: 'input_data.csv', 
        fileType: 'CSV', 
        fileSize: 2048576, 
        uploadTime: '20220102 09:15:20' 
      },
      { 
        key: 'f2', 
        fileId: 'F002', 
        fileName: 'config.json', 
        fileType: 'JSON', 
        fileSize: 4096, 
        uploadTime: '20220102 09:16:30' 
      }
    ];

    const job = jobData.value.find(j => j.jobId === jobId);
    if (job) {
      job.jobFiles = mockFiles;
    }

    return mockFiles;
  } finally {
    loadingFiles.value[jobId] = false;
  }
};

// 重試 Job
const retryJob = async (jobId) => {
  try {
    await api.post(`/jobs/${jobId}/retry`);
    message.success(`Job ${jobId} 重試成功`);
    
    // 重新載入列表
    await fetchJobs();
  } catch (error) {
    console.error('重試 Job 失敗:', error);
    message.error('重試 Job 失敗');
  }
};

// 取消 Job
const cancelJob = async (jobId) => {
  try {
    await api.post(`/jobs/${jobId}/cancel`);
    message.success(`Job ${jobId} 已取消`);
    
    // 重新載入列表
    await fetchJobs();
  } catch (error) {
    console.error('取消 Job 失敗:', error);
    message.error('取消 Job 失敗');
  }
};

// 刪除 Job
const deleteJob = async (jobId) => {
  try {
    await api.delete(`/jobs/${jobId}`);
    message.success(`Job ${jobId} 已刪除`);
    
    // 重新載入列表
    await fetchJobs();
  } catch (error) {
    console.error('刪除 Job 失敗:', error);
    message.error('刪除 Job 失敗');
  }
};

// ============================================
// 事件處理函數
// ============================================

// 查詢按鈕
const handleSearch = async () => {
  paginationConfig.value.current = 1; // 重置到第一頁
  await fetchJobs();
};

// 重新整理按鈕
const handleRefresh = async () => {
  await fetchJobs();
};

// 表格分頁變更
const handleTableChange = (pagination) => {
  paginationConfig.value.current = pagination.current;
  paginationConfig.value.pageSize = pagination.pageSize;
  fetchJobs();
};

// 展開行
const handleExpand = async (expanded, record) => {
  if (expanded) {
    expandedRowKeys.value = [record.key];
    
    // 如果檔案列表為空，則載入
    if (!record.jobFiles || record.jobFiles.length === 0) {
      await fetchJobFiles(record.jobId);
    }
  } else {
    expandedRowKeys.value = [];
  }
};

// Job 操作
const handleJobRetry = (job) => {
  Modal.confirm({
    title: '確認重試',
    content: `確定要重試 Job「${job.jobId}」嗎？`,
    okText: '確定',
    cancelText: '取消',
    onOk: async () => {
      await retryJob(job.jobId);
    }
  });
};

const handleJobCancel = (job) => {
  Modal.confirm({
    title: '確認取消',
    content: `確定要取消 Job「${job.jobId}」嗎？`,
    okText: '確定',
    cancelText: '取消',
    onOk: async () => {
      await cancelJob(job.jobId);
    }
  });
};

const handleJobDelete = (job) => {
  Modal.confirm({
    title: '確認刪除',
    content: `確定要刪除 Job「${job.jobId}」嗎？此操作無法復原。`,
    okText: '確定刪除',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      await deleteJob(job.jobId);
    }
  });
};

// ============================================
// 工具函數
// ============================================

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

// ============================================
// 生命週期
// ============================================

onMounted(async () => {
  // 頁面載入時取得資料
  await fetchJobs();
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