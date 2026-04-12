<template>
  <div class="container mt-4">
    <h2>My Applications</h2>
    <button @click="exportCSV" class="btn btn-primary mb-3" :disabled="exporting">
      {{ exporting ? 'Exporting...' : 'Export as CSV' }}
    </button>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Company</th>
          <th>Job Title</th>
          <th>Applied On</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="app in applications" :key="app.id">
          <td>{{ app.company_name }}</td>
          <td>{{ app.job_title }}</td>
          <td>{{ formatDate(app.applied_on) }}</td>
          <td>{{ app.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from '../plugins/axios'

export default {
  name: 'StudentApplications',
  data() {
    return {
      applications: [],
      pollingInterval: null,
      exporting: false
    }
  },
  beforeUnmount() {
    this.clearPolling()
  },
  mounted() {
    this.fetchApplications()
  },
  methods: {
    clearPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    },
    async fetchApplications() {
      try {
        const res = await axios.get('/student/applications')
        this.applications = res.data
      } catch (err) {
        console.error(err)
      }
    },
    formatDate(dateStr) {
      const d = new Date(dateStr)
      return d.toLocaleDateString()
    },
    async exportCSV() {
      this.exporting = true
      try {
        const res = await axios.post('/student/export/applications')
        const taskId = res.data.task_id
        this.clearPolling()
        this.pollingInterval = setInterval(async () => {
          try {
            const statusRes = await axios.get(`/student/export/status/${taskId}`)
            if (statusRes.data.status === 'SUCCESS') {
              this.clearPolling()
              this.exporting = false
              const result = statusRes.data.result
              const blob = new Blob([result.csv], { type: 'text/csv' })
              const link = document.createElement('a')
              link.href = URL.createObjectURL(blob)
              link.download = result.filename
              link.click()
              URL.revokeObjectURL(link.href)
            } else if (statusRes.data.status === 'FAILURE') {
              this.clearPolling()
              this.exporting = false
              alert('Export failed: ' + (statusRes.data.error || 'Unknown error'))
            }
          } catch (err) {
            this.clearPolling()
            this.exporting = false
            alert('Error checking export status')
          }
        }, 2000)
      } catch (err) {
        this.exporting = false
        alert('Error starting export')
      }
    }
  }
}
</script>
