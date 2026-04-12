<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <h2 class="text-center">Company Registration</h2>
        <form @submit.prevent="register">
          <div class="mb-3">
            <label for="company_name" class="form-label">Company Name</label>
            <input type="text" class="form-control" id="company_name" v-model="form.company_name" required>
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
            <label for="hr_contact" class="form-label">HR Contact</label>
            <input type="text" class="form-control" id="hr_contact" v-model="form.hr_contact">
          </div>
          <div class="mb-3">
            <label for="website" class="form-label">Website</label>
            <input type="url" class="form-control" id="website" v-model="form.website">
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
  name: 'RegisterCompany',
  data() {
    return {
      form: {
        company_name: '',
        email: '',
        password: '',
        hr_contact: '',
        website: ''
      },
      loading: false
    }
  },
  methods: {
    async register() {
      this.loading = true
      try {
        await axios.post('/auth/register/company', this.form)
        alert('Registration successful! Await admin approval.')
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
