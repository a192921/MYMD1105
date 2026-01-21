import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 或使用 true,允許外部訪問
    port: 80, // 默認端口,可以自定義
    strictPort: false, // 端口被佔用時自動嘗試下一個
    open: true, // 啟動時自動打開瀏覽器
  }
})
