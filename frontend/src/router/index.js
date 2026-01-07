import Vue from 'vue';
import Router from 'vue-router';
import Home from '@/views/Home.vue';
import Login from '@/views/Login.vue';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/upload',
      name: 'Upload',
      component: () => import('@/views/Upload.vue')
    },
    {
      path: '/files',
      name: 'Files',
      component: () => import('@/views/Files.vue')
    },
    {
      path: '/metrics',
      name: 'Metrics',
      component: () => import('@/views/Metrics.vue')
    },
    {
      path: '/reports',
      name: 'Reports',
      component: () => import('@/views/Reports.vue')
    }
  ]
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('jwt');
  if (to.path !== '/login' && !token) {
    return next('/login');
  }
  return next();
});

export default router;
