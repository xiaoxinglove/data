import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('./views/Dashboard.vue'),
  },
  {
    path: '/knowledge',
    name: 'knowledge',
    component: () => import('./views/Knowledge.vue'),
  },
  {
    path: '/workflow',
    name: 'workflow',
    component: () => import('./views/Workflow.vue'),
  },
  {
    path: '/evaluation',
    name: 'evaluation',
    component: () => import('./views/Evaluation.vue'),
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
