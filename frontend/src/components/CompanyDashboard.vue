<template>
  <div class="container mt-4">
    <h2>Company Dashboard</h2>
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">{{ company.company_name }}</h5>
        <p class="card-text">HR Contact: {{ company.hr_contact }}</p>
        <p class="card-text">Website: {{ company.website }}</p>
        <router-link to="/company/profile" class="btn btn-primary">Edit Profile</router-link>
      </div>
    </div>

    <h3>Your Placement Drives</h3>
    <router-link to="/company/drives/create" class="btn btn-success mb-3">Create New Drive</router-link>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Job Title</th>
          <th>Deadline</th>
          <th>Status</th>
          <th>Applicants</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="drive in drives" :key="drive.id">
          <td>{{ drive.job_title }}</td>
          <td>{{ formatDate(drive.deadline) }}</td>
          <td>{{ drive.status }}</td>
          <td>{{ drive.applicants_count }}</td>
          <td>
            <router-link :to="`/company/drives/${drive.id}/applications`" class="btn btn-info btn-sm me-1">View Applications</router-link>
            <router-link v-if="drive.status !== 'closed'" :to="`/company/drives/${drive.id}/edit`" class="btn btn-primary btn-sm me-1">Edit</router-link>
            <button v-if="drive.status !== 'closed'" @click="closeDrive(drive.id)" class="btn btn-warning btn-sm">Close</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from '../plugins/axios'

export default {
  name: 'CompanyDashboard',
  data() {
    return {
      company: {},
      drives: []
    }
  },
  mounted() {
    this.fetchDashboard()
  },
  methods: {
    async fetchDashboard() {
      try {
        const res = await axios.get('/company/dashboard')
        this.company = res.data.company
        this.drives = res.data.drives
      } catch (err) {
        console.error(err)
      }
    },
    async closeDrive(id) {
      if (!confirm('Close this drive? Applications will no longer be accepted.')) return
      try {
        await axios.post(`/company/drives/${id}/close`)
        this.fetchDashboard()
      } catch (err) {
        alert('Error closing drive')
      }
    },
    formatDate(dateStr) {
      const d = new Date(dateStr)
      return d.toLocaleDateString()
    }
  }
}
</script>
