<template>
  <div class="container mt-4">
    <h2>Edit Placement Drive</h2>
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
        <input type="text" class="form-control" id="eligibility" v-model="form.eligibility">
      </div>
      <div class="mb-3">
        <label for="deadline" class="form-label">Application Deadline</label>
        <input type="date" class="form-control" id="deadline" v-model="form.deadline" required>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? 'Saving...' : 'Save Changes' }}</button>
    </form>
  </div>
</template>

<script>
import axios from '../plugins/axios'

export default {
  name: 'EditDrive',
  data() {
    return {
      form: {
        job_title: '',
        description: '',
        eligibility: '',
        deadline: ''
      },
      loading: false,
      driveId: null
    }
  },
  mounted() {
    this.driveId = this.$route.params.id
    this.fetchDrive()
  },
  methods: {
    async fetchDrive() {
      try {
        const res = await axios.get(`/company/drives/${this.driveId}`)
        this.form = res.data
      } catch (err) {
        console.error(err)
        alert('Drive not found')
        this.$router.push('/company/drives')
      }
    },
    async submit() {
      this.loading = true
      try {
        await axios.put(`/company/drives/${this.driveId}`, this.form)
        alert('Drive updated')
        this.$router.push('/company/drives')
      } catch (err) {
        alert(err.response?.data?.msg || 'Error updating drive')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
