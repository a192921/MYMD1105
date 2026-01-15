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
          <a-input
            v-model:value="actionFilter"
            placeholder="輸入 Action"
            style="width: 200px"
            allow-clear
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
        :columns="resizableColumns"
        :data-source="filteredAuditData"
        :pagination="paginationConfig"
        :loading="loading"
        :scroll="{ y: 'calc(100vh - 380px)', x: 'max-content' }"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'detail'">
            <span :class="{'detail-link': isLink(record.detail)}">
              {{ record.detail || '-' }}
            </span>
          </template>
          <template v-else-if="column.key === 'outcome'">
            <span>{{ record.outcome || '-' }}</span>
          </template>
          <template v-else-if="column.key === 'resultCode'">
            <span>{{ record.resultCode || '-' }}</span>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue';
import { CalendarOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import dayjs from 'dayjs';
import { api } from '../utils/api';

// ============================================
// 狀態管理
// ============================================
const loading = ref(false);
const startDate = ref(dayjs());
const endDate = ref(dayjs());
const actionFilter = ref('');
const pageSize = ref(20);
const currentPage = ref(1);
const totalRecords = ref(0);

const pageSizeOptions = [
  { label: '20 筆/頁', value: 20 },
  { label: '50 筆/頁', value: 50 },
  { label: '100 筆/頁', value: 100 },
  { label: '200 筆/頁', value: 200 }
];

const auditData = ref([]);

// ============================================
// 計算屬性
// ============================================

// 過濾後的資料（根據 action 篩選）
const filteredAuditData = computed(() => {
  if (!actionFilter.value || !actionFilter.value.trim()) {
    return auditData.value;
  }
  
  const filterText = actionFilter.value.toLowerCase().trim();
  return auditData.value.filter(item => 
    item.action.toLowerCase().includes(filterText)
  );
});

// 分頁配置
const paginationConfig = computed(() => ({
  current: currentPage.value,
  pageSize: pageSize.value,
  total: totalRecords.value,
  showSizeChanger: false,
  showTotal: (total) => `共 ${total} 筆記錄`,
  showQuickJumper: true,
}));

// 動態產生篩選選項
const requestIdFilters = computed(() => {
  const uniqueIds = [...new Set(auditData.value.map(item => item.requestId))];
  return uniqueIds.filter(id => id !== '-').map(id => ({
    text: id,
    value: id
  })).sort((a, b) => a.text.localeCompare(b.text));
});

const userIdFilters = computed(() => {
  const uniqueIds = [...new Set(auditData.value.map(item => item.userId))];
  return uniqueIds.filter(id => id !== '-').map(id => ({
    text: id,
    value: id
  })).sort((a, b) => a.text.localeCompare(b.text));
});

const useTypeFilters = computed(() => {
  const uniqueTypes = [...new Set(auditData.value.map(item => item.useType))];
  return uniqueTypes.filter(type => type !== '-').map(type => ({
    text: type,
    value: type
  })).sort((a, b) => a.text.localeCompare(b.text));
});

const actionFilters = computed(() => {
  const uniqueActions = [...new Set(auditData.value.map(item => item.action))];
  return uniqueActions.filter(action => action !== '-').map(action => ({
    text: action,
    value: action
  })).sort((a, b) => a.text.localeCompare(b.text));
});

// ============================================
// 欄位寬度調整功能
// ============================================

const resizeColumn = (width, column) => {
  column.width = Math.max(width, 80); // 最小寬度 80px
};

let startX = 0;
let startWidth = 0;
let activeColumn = null;

const onMouseMove = (e) => {
  if (!activeColumn) return;
  resizeColumn(startWidth + e.clientX - startX, activeColumn);
};

const onMouseUp = () => {
  activeColumn = null;
  document.removeEventListener('mousemove', onMouseMove);
  document.removeEventListener('mouseup', onMouseUp);
};

// ============================================
// 表格欄位定義
// ============================================

const resizableColumns = reactive([
  { 
    title: 'Log ID', 
    dataIndex: 'logId', 
    key: 'logId',
    width: 100,
    sorter: (a, b) => String(a.logId || '').localeCompare(String(b.logId || '')),
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        startX = e.clientX;
        startWidth = column.width;
        activeColumn = column;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      },
    }),
  },
  { 
    title: 'Request ID', 
    dataIndex: 'requestId', 
    key: 'requestId',
    width: 150,
    sorter: (a, b) => String(a.requestId || '').localeCompare(String(b.requestId || '')),
    filters: requestIdFilters.value,
    filterSearch: true,
    onFilter: (value, record) => record.requestId === value,
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        startX = e.clientX;
        startWidth = column.width;
        activeColumn = column;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      },
    }),
  },
  { 
    title: 'User ID', 
    dataIndex: 'userId', 
    key: 'userId',
    width: 120,
    sorter: (a, b) => String(a.userId || '').localeCompare(String(b.userId || '')),
    filters: userIdFilters.value,
    filterSearch: true,
    onFilter: (value, record) => record.userId === value,
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        startX = e.clientX;
        startWidth = column.width;
        activeColumn = column;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      },
    }),
  },
  { 
    title: 'Use Type', 
    dataIndex: 'useType', 
    key: 'useType',
    width: 120,
    sorter: (a, b) => String(a.useType || '').localeCompare(String(b.useType || '')),
    filters: useTypeFilters.value,
    filterSearch: true,
    onFilter: (value, record) => record.useType === value,
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        startX = e.clientX;
        startWidth = column.width;
        activeColumn = column;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      },
    }),
  },
  { 
    title: 'Action', 
    dataIndex: 'action', 
    key: 'action',
    width: 150,
    sorter: (a, b) => String(a.action || '').localeCompare(String(b.action || '')),
    filters: actionFilters.value,
    filterSearch: true,
    onFilter: (value, record) => record.action === value,
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        startX = e.clientX;
        startWidth = column.width;
        activeColumn = column;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      },
    }),
  },
  { 
    title: 'Outcome', 
    dataIndex: 'outcome', 
    key: 'outcome',
    width: 120,
    sorter: (a, b) => String(a.outcome || '').localeCompare(String(b.outcome || '')),
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        startX = e.clientX;
        startWidth = column.width;
        activeColumn = column;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      },
    }),
  },
  { 
    title: 'Result Code', 
    dataIndex: 'resultCode', 
    key: 'resultCode',
    width: 120,
    sorter: (a, b) => String(a.resultCode || '').localeCompare(String(b.resultCode || '')),
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        startX = e.clientX;
        startWidth = column.width;
        activeColumn = column;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      },
    }),
  },
  { 
    title: 'Detail', 
    dataIndex: 'detail', 
    key: 'detail',
    width: 200,
    sorter: (a, b) => String(a.detail || '').localeCompare(String(b.detail || '')),
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        startX = e.clientX;
        startWidth = column.width;
        activeColumn = column;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      },
    }),
  },
  { 
    title: 'Timestamp', 
    dataIndex: 'timestamp', 
    key: 'timestamp',
    width: 200,
    sorter: (a, b) => {
      const dateA = dayjs(a.timestamp, 'YYYY-MM-DD HH:mm:ss');
      const dateB = dayjs(b.timestamp, 'YYYY-MM-DD HH:mm:ss');
      return dateA.valueOf() - dateB.valueOf();
    },
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        startX = e.clientX;
        startWidth = column.width;
        activeColumn = column;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      },
    }),
  }
]);

// ============================================
// 工具函數
// ============================================

// 格式化時間戳記
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-';
  
  try {
    const date = dayjs(timestamp);
    if (date.isValid()) {
      return date.format('YYYY-MM-DD HH:mm:ss');
    }
    return timestamp;
  } catch (error) {
    return timestamp;
  }
};

// 判斷是否為連結
const isLink = (detail) => {
  if (!detail || detail === '-') return false;
  return detail.includes('Upload_image') || detail.includes('upload');
};

// ============================================
// API 呼叫函數
// ============================================

const fetchAuditLogs = async () => {
  loading.value = true;
  
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value
    };

    if (startDate.value) {
      params.startDate = dayjs(startDate.value).format('YYYY-MM-DD');
    }
    if (endDate.value) {
      params.endDate = dayjs(endDate.value).format('YYYY-MM-DD');
    }

    const response = await api.get('/api/audit-logs', { params });

    console.log('審計記錄 API 回應:', response.data);

    if (response.data && response.data.status && response.data.data) {
      const { useLogs = [], total = 0 } = response.data.data;

      auditData.value = useLogs.map((item, index) => ({
        key: item.logId || `${currentPage.value}-${index}`,
        logId: String(item.logId || '-'),
        requestId: String(item.requestId || '-'),
        userId: String(item.userId || '-'),
        useType: String(item.useType || '-'),
        action: String(item.action || '-'),
        outcome: String(item.outcome || '-'),
        resultCode: String(item.resultCode || '-'),
        detail: String(item.detail || '-'),
        timestamp: formatTimestamp(item.timestamp)
      }));

      totalRecords.value = total;

      message.success('審計記錄載入成功');
    } else {
      throw new Error('API 回應格式不正確');
    }

  } catch (error) {
    console.error('獲取審計記錄失敗:', error);
    message.error('獲取審計記錄失敗，請稍後再試');
    
    // 使用假資料
    auditData.value = [
      { 
        key: '1', 
        logId: '1', 
        requestId: 'req-1', 
        userId: '1', 
        useType: '-', 
        action: 'TestAction', 
        outcome: '-', 
        resultCode: '-', 
        detail: '-', 
        timestamp: '2022-01-02 22:48:30' 
      },
      { 
        key: '2', 
        logId: '2', 
        requestId: 'req-2', 
        userId: '2', 
        useType: 'upload', 
        action: 'upload', 
        outcome: 'success', 
        resultCode: '200', 
        detail: 'upload file', 
        timestamp: '2022-01-03 10:20:15' 
      },
      { 
        key: '3', 
        logId: '3', 
        requestId: 'req-3', 
        userId: '3', 
        useType: 'login', 
        action: 'login', 
        outcome: 'success', 
        resultCode: '200', 
        detail: 'user login', 
        timestamp: '2022-01-04 09:15:42' 
      },
    ];
    totalRecords.value = 100;
  } finally {
    loading.value = false;
  }
};

// ============================================
// 事件處理函數
// ============================================

// 處理查詢按鈕點擊
const handleSearch = () => {
  if (startDate.value && endDate.value) {
    if (dayjs(startDate.value).isAfter(dayjs(endDate.value))) {
      message.warning('開始日期不能晚於結束日期');
      return;
    }
  }

  currentPage.value = 1;
  actionFilter.value = '';
  fetchAuditLogs();
};

// 處理表格變更（分頁、排序、篩選）
const handleTableChange = (pagination, filters, sorter) => {
  console.log('表格變更:', { pagination, filters, sorter });
  currentPage.value = pagination.current;
  fetchAuditLogs();
};

// ============================================
// 生命週期
// ============================================

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

/* 拖曳線樣式 */
.ant-table-thead th {
  position: relative;
}

.ant-table-thead th::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  z-index: 10;
}

.ant-table-thead th::after:hover {
  background: rgba(24, 144, 255, 0.3);
}

/* 讓 detail 欄位中的連結顯示為紅色底線 */
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