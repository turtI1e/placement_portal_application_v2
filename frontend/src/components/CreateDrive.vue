<template>
  <div class="container mt-4">
    <h2>Create Placement Drive</h2>
    <form @submit.prevent="submit">
      <div class="mb-3">
        <label for="job_title" class="form-label">Job Title</label>
        <input type="text" class="form-control" id="job_title" v-model="form.job_title" required>
      </div>
      <div class="mb-3">
        <label for="description" class="form-label">Description</label>
        <textarea class="form-control" id="description" rows="3" v-model="form.description" required></textarea>
      </div>
      <div class="mb-3">
        <label for="eligibility" class="form-label">Eligibility Criteria</label>
        <input type="text" class="form-control" id="eligibility" v-model="form.eligibility" placeholder="e.g., CS,IT; CGPA>7">
      </div>
      <div class="mb-3">
        <label for="deadline" class="form-label">Application Deadline</label>
        <input type="date" class="form-control" id="deadline" v-model="form.deadline" required>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? 'Creating...' : 'Create Drive' }}</button>
    </form>
  </div>
</template>

<script>
import axios from '../plugins/axios'

export default {
  name: 'CreateDrive',
  data() {
    return {
      form: {
        job_title: '',
        description: '',
        eligibility: '',
        deadline: ''
      },
      loading: false
    }
  },
  methods: {
    async submit() {
      this.loading = true
      try {
        await axios.post('/company/drives', this.form)
        alert('Drive created, pending admin approval')
        this.$router.push('/company/drives')
      } catch (err) {
        alert(err.response?.data?.msg || 'Error creating drive')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
