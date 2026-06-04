import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Unified',
      component: () => import('../views/PageUnified.vue'),
    },
    {
      path: '/documents',
      name: 'Documents',
      component: () => import('../views/Documents.vue'),
    },
    {
      path: '/chat',
      name: 'Chat',
      component: () => import('../views/Chat.vue'),
    },
  ],
})

export default router
