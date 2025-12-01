<template>
  <div class="page-container">
    <h1 class="page-title">系統總覽（Job統計）</h1>
    
    <div class="section-title">Job數據</div>

    <a-row :gutter="24" class="stats-row">
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" hoverable>
          <div class="stat-label">用戶總數</div>
          <div class="stat-value blue">{{ stats.totalCustomer }}</div>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" hoverable>
          <div class="stat-label">JOB 總數</div>
          <div class="stat-value orange">{{ stats.totalJob }}</div>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" hoverable>
          <div class="stat-label">Job 執行中</div>
          <div class="stat-value gray">{{ stats.jobRunning }}</div>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" hoverable>
          <div class="stat-label">Job 執行失敗</div>
          <div class="stat-value yellow">{{ stats.jobFailed }}</div>
        </a-card>
      </a-col>
    </a-row>

    <!-- <a-card title="更新數據" class="update-card">
      <a-row :gutter="16">
        <a-col :xs="24" :sm="12" :lg="6">
          <a-form-item label="用戶總數">
            <a-input-number v-model:value="stats.totalCustomer" :min="0" style="width: 100%" />
          </a-form-item>
        </a-col>
        <a-col :xs="24" :sm="12" :lg="6">
          <a-form-item label="JOB 總數">
            <a-input-number v-model:value="stats.totalJob" :min="0" style="width: 100%" />
          </a-form-item>
        </a-col>
        <a-col :xs="24" :sm="12" :lg="6">
          <a-form-item label="執行中">
            <a-input-number v-model:value="stats.jobRunning" :min="0" style="width: 100%" />
          </a-form-item>
        </a-col>
        <a-col :xs="24" :sm="12" :lg="6">
          <a-form-item label="失敗">
            <a-input-number v-model:value="stats.jobFailed" :min="0" style="width: 100%" />
          </a-form-item>
        </a-col>
      </a-row>
    </a-card> -->
  </div>
</template>

<script setup>
// import { ref } from 'vue';
import { api } from '../utils/api';
import { onMounted, ref } from 'vue';

const stats = ref({
  totalCustomer: 50,
  totalJob: 30,
  jobRunning: 5,
  jobFailed: 125
});


onMounted(async () => {
  try {
    // API 會自動帶上 JWT Token
    const response = await api.get('/dashboard/stats');
    stats.value = response.data;
  } catch (error) {
    console.error('取得統計資料失敗:', error);
  }
});

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

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
}

.stats-row {
  margin-bottom: 32px;
}

.stat-card {
  text-align: center;
  padding: 16px 0;
}

.stat-label {
  font-size: 16px;
  color: #6b7280;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 56px;
  font-weight: bold;
}

.stat-value.blue { color: #3b82f6; }
.stat-value.orange { color: #f97316; }
.stat-value.gray { color: #9ca3af; }
.stat-value.yellow { color: #facc15; }

.update-card {
  margin-top: 32px;
}
</style>