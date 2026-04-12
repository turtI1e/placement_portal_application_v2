<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <router-link class="navbar-brand" to="/">Placement Portal</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li v-if="!isAuthenticated" class="nav-item">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li v-if="!isAuthenticated" class="nav-item">
            <router-link class="nav-link" to="/register/student">Student Register</router-link>
          </li>
          <li v-if="!isAuthenticated" class="nav-item">
            <router-link class="nav-link" to="/register/company">Company Register</router-link>
          </li>

          <template v-if="isAuthenticated && role === 'admin'">
            <li class="nav-item"><router-link class="nav-link" to="/admin/dashboard">Dashboard</router-link></li>
          </template>

          <template v-if="isAuthenticated && role === 'company'">
            <li class="nav-item"><router-link class="nav-link" to="/company/dashboard">Dashboard</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/company/profile">Profile</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/company/drives">My Drives</router-link></li>
          </template>

          <template v-if="isAuthenticated && role === 'student'">
            <li class="nav-item"><router-link class="nav-link" to="/student/dashboard">Dashboard</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/student/profile">Profile</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/student/drives">Drives</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/student/applications">Applications</router-link></li>
          </template>

          <li v-if="isAuthenticated" class="nav-item">
            <button class="btn btn-link nav-link" @click="handleLogout">Logout</button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'AppNavbar',
  computed: {
    ...mapGetters(['isAuthenticated', 'userRole']),
    role() {
      return this.userRole
    }
  },
  methods: {
    ...mapActions(['logout']),
    handleLogout() {
      this.logout()
      this.$router.push('/login')
    }
  }
}
</script>
