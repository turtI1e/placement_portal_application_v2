<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <h2 class="text-center">Student Registration</h2>
        <form @submit.prevent="register">
          <div class="mb-3">
            <label for="name" class="form-label">Full Name</label>
            <input type="text" class="form-control" id="name" v-model="form.name" required>
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input type="email" class="form-control" id="email" v-model="form.email" required>
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input type="password" class="form-control" id="password" v-model="form.password" required>
          </div>
          <div class="mb-3">
            <label for="contact" class="form-label">Contact</label>
            <input type="text" class="form-control" id="contact" v-model="form.contact">
          </div>
          <div class="mb-3">
            <label for="branch" class="form-label">Branch</label>
            <input type="text" class="form-control" id="branch" v-model="form.branch">
          </div>
          <div class="mb-3">
            <label for="year" class="form-label">Year</label>
            <input type="number" class="form-control" id="year" v-model="form.year">
          </div>
          <div class="mb-3">
            <label for="cgpa" class="form-label">CGPA</label>
            <input type="number" step="0.01" class="form-control" id="cgpa" v-model="form.cgpa">
          </div>
          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? 'Registering...' : 'Register' }}
          </button>
        </form>
        <div class="mt-3 text-center">
          Already have an account? <router-link to="/login">Login</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '../plugins/axios'

export default {
  name: 'RegisterStudent',
  data() {
    return {
      form: {
        name: '',
        email: '',
        password: '',
        contact: '',
        branch: '',
        year: '',
        cgpa: ''
      },
      loading: false
    }
  },
  methods: {
    async register() {
      this.loading = true
      try {
        await axios.post('/auth/register/student', this.form)
        alert('Registration successful! Please login.')
        this.$router.push('/login')
      } catch (error) {
        const msg = error.response?.data?.msg || 'Registration failed'
        alert(msg)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
