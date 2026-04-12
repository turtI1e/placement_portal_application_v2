<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <h2 class="text-center">Login</h2>
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="email" class="form-label">Email address</label>
            <input type="email" class="form-control" id="email" v-model="email" required>
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input type="password" class="form-control" id="password" v-model="password" required>
          </div>
          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>
        <div class="mt-3 text-center">
          <p>Don't have an account?</p>
          <router-link to="/register/student" class="btn btn-link">Register as Student</router-link>
          <router-link to="/register/company" class="btn btn-link">Register as Company</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      loading: false
    }
  },
  methods: {
    ...mapActions(['login']),
    async handleLogin() {
      this.loading = true
      try {
        const role = await this.login({ email: this.email, password: this.password })
        this.$router.push(`/${role}/dashboard`)
      } catch (error) {
        const msg = error.response?.data?.msg || 'Login failed'
        alert(msg)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
