import { createRouter, createWebHistory } from 'vue-router';
import { isAuthenticated } from '../utils/auth';
import Login from '../views/Login.vue';
import Dashboard from '../views/Dashboard.vue';

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守衛：檢查認證狀態
router.beforeEach(async (to, from, next) => {
  const authenticated = await isAuthenticated();
  
  if (to.meta.requiresAuth && !authenticated) {
    // 需要認證但未登入，跳轉到登入頁
    next('/login');
  } else if (to.path === '/login' && authenticated) {
    // 已登入但訪問登入頁，跳轉到 Dashboard
    next('/dashboard');
  } else {
    next();
  }
});

export default router;
