<template>
  <div class="login-container">
    <a-card class="login-card" :bordered="false">
      <div class="logo-section">
        <div class="logo-icon">
          <ToolOutlined style="font-size: 32px; color: white" />
        </div>
        <div class="logo-text">
          <div class="logo-title">MYMD</div>
          <div class="logo-subtitle">Admin System</div>
        </div>
      </div>

      <a-form
        :model="loginForm"
        @finish="handleLogin"
        layout="vertical"
      >
        <a-form-item
          label="Username"
          name="username"
          :rules="[{ required: true, message: '請輸入用戶名稱!' }]"
        >
          <a-input
            v-model:value="loginForm.username"
            size="large"
            placeholder="請輸入用戶名稱"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          label="Password"
          name="password"
          :rules="[{ required: true, message: '請輸入密碼!' }]"
        >
          <a-input-password
            v-model:value="loginForm.password"
            size="large"
            placeholder="請輸入密碼"
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">
            登入
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { UserOutlined, LockOutlined, ToolOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';

const router = useRouter();
const loading = ref(false);

const loginForm = ref({
  username: '',
  password: ''
});

const handleLogin = () => {
  loading.value = true;
  // 模擬登入
  setTimeout(() => {
    loading.value = false;
    message.success('登入成功！');
    router.push('/dashboard');
  }, 1000);
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #1f1dba 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border-radius: 12px;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #1f1dba 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.logo-text {
  text-align: center;
}

.logo-title {
  font-size: 36px;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: 2px;
}

.logo-subtitle {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}
</style>