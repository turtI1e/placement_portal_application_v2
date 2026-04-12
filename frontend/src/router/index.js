import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import RegisterStudent from '../components/RegisterStudent.vue'
import RegisterCompany from '../components/RegisterCompany.vue'
import store from '../store'

const routes = [
  { path: '/login', component: Login },
  { path: '/register/student', component: RegisterStudent },
  { path: '/register/company', component: RegisterCompany },
  
  // Admin routes
  { path: '/admin/dashboard', component: () => import('../components/AdminDashboard.vue'), meta: { requiresAuth: true, role: 'admin' } },
  
  // Company routes
  { path: '/company/dashboard', component: () => import('../components/CompanyDashboard.vue'), meta: { requiresAuth: true, role: 'company' } },
  { path: '/company/profile', component: () => import('../components/CompanyProfile.vue'), meta: { requiresAuth: true, role: 'company' } },
  { path: '/company/drives', component: () => import('../components/CompanyDrives.vue'), meta: { requiresAuth: true, role: 'company' } },
  { path: '/company/drives/create', component: () => import('../components/CreateDrive.vue'), meta: { requiresAuth: true, role: 'company' } },
  { path: '/company/drives/:id/edit', component: () => import('../components/EditDrive.vue'), meta: { requiresAuth: true, role: 'company' } },
  { path: '/company/drives/:id/applications', component: () => import('../components/DriveApplications.vue'), meta: { requiresAuth: true, role: 'company' } },
  
  // Student routes
  { path: '/student/dashboard', component: () => import('../components/StudentDashboard.vue'), meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/profile', component: () => import('../components/StudentProfile.vue'), meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/drives', component: () => import('../components/StudentDrives.vue'), meta: { requiresAuth: true, role: 'student' } },
  { path: '/student/applications', component: () => import('../components/StudentApplications.vue'), meta: { requiresAuth: true, role: 'student' } },
  
  { path: '/', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiredRole = to.meta.role
  const token = sessionStorage.getItem('access_token')
  const role = sessionStorage.getItem('user_role')

  if (requiresAuth) {
    if (!token) {
      next('/login')
    } else if (requiredRole && requiredRole !== role) {
      next('/login')
    } else {
      next()
    }
  } else {
    if (token && (to.path === '/login' || to.path === '/')) {
      if (role === 'admin') next('/admin/dashboard')
      else if (role === 'company') next('/company/dashboard')
      else if (role === 'student') next('/student/dashboard')
      else next()
    } else {
      next()
    }
  }
})

export default router
