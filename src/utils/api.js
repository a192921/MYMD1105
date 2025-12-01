import axios from 'axios';
import { getAccessToken } from './auth';
import { message } from 'ant-design-vue';
import router from '../router';

// 建立 axios 實例
const apiClient = axios.create({
  baseURL: 'https://your-api-domain.com/api', // 你的 API 基礎 URL
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 請求攔截器：自動加入 JWT Token
apiClient.interceptors.request.use(
  async (config) => {
    // 取得 Access Token
    const token = await getAccessToken();
    
    if (token) {
      // 將 Token 加入 Authorization Header
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 回應攔截器：處理錯誤
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Token 過期或無效，跳轉到登入頁
          message.error('登入已過期，請重新登入');
          router.push('/login');
          break;
        case 403:
          message.error('沒有權限訪問此資源');
          break;
        case 404:
          message.error('請求的資源不存在');
          break;
        case 500:
          message.error('伺服器錯誤，請稍後再試');
          break;
        default:
          message.error('請求失敗: ' + error.message);
      }
    } else {
      message.error('網路錯誤，請檢查連線');
    }
    return Promise.reject(error);
  }
);

// API 方法封裝
export const api = {
  // GET 請求
  get: (url, params = {}) => {
    return apiClient.get(url, { params });
  },

  // POST 請求
  post: (url, data = {}) => {
    return apiClient.post(url, data);
  },

  // PUT 請求
  put: (url, data = {}) => {
    return apiClient.put(url, data);
  },

  // DELETE 請求
  delete: (url) => {
    return apiClient.delete(url);
  },

  // PATCH 請求
  patch: (url, data = {}) => {
    return apiClient.patch(url, data);
  }
};

export default apiClient;