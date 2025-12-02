// router/index.js
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    }
  ]
});

// 路由守衛
router.beforeEach((to, from, next) => {
  const isAuthenticated = sessionStorage.getItem('is_authenticated') === 'true';
  
  console.log('路由守衛檢查:', {
    to: to.path,
    from: from.path,
    isAuthenticated
  });

  if (to.meta.requiresAuth && !isAuthenticated) {
    // 需要認證但未登入,跳轉到登入頁
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    // 已登入卻訪問登入頁,跳轉到 dashboard
    next('/dashboard');
  } else {
    next();
  }
});

export default router;
```

---

## 🔧 Azure Portal 設定檢查

確認 Azure AD 的 Redirect URI 設定:

1. 進入 Azure Portal → App registrations
2. 選擇您的應用程式
3. 點選 **Authentication**
4. 在 **Single-page application** 區域,確認有以下 URI:
```
   http://localhost:5173
   http://localhost:5173/dashboard
```
5. 如果是生產環境,也要加上:
```
   https://yourdomain.com
   https://yourdomain.com/dashboard