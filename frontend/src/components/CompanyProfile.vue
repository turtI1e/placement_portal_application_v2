<template>
  <div class="container mt-4">
    <h2>Edit Company Profile</h2>
    <form @submit.prevent="updateProfile">
      <div class="mb-3">
        <label for="company_name" class="form-label">Company Name</label>
        <input type="text" class="form-control" id="company_name" v-model="form.company_name" required>
      </div>
      <div class="mb-3">
        <label for="hr_contact" class="form-label">HR Contact</label>
        <input type="text" class="form-control" id="hr_contact" v-model="form.hr_contact">
      </div>
      <div class="mb-3">
        <label for="website" class="form-label">Website</label>
        <input type="url" class="form-control" id="website" v-model="form.website">
      </div>
      <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? 'Saving...' : 'Save Changes' }}</button>
    </form>
  </div>
</template>

<script>
import axios from '../plugins/axios'

export default {
  name: 'CompanyProfile',
  data() {
    return {
      form: {
        company_name: '',
        hr_contact: '',
        website: ''
      },
      loading: false
    }
  },
  mounted() {
    this.fetchProfile()
  },
  methods: {
    async fetchProfile() {
      try {
        const res = await axios.get('/company/profile')
        this.form = res.data
      } catch (err) {
        console.error(err)
      }
    },
    async updateProfile() {
      this.loading = true
      try {
        await axios.put('/company/profile', this.form)
        alert('Profile updated')
        this.$router.push('/company/dashboard')
      } catch (err) {
        alert('Error updating profile')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
