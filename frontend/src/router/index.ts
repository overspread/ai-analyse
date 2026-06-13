import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/documents',
    },
    {
      path: '/documents',
      name: 'documents',
      component: () => import('../views/Documents.vue'),
    },
  ],
})

export default router
