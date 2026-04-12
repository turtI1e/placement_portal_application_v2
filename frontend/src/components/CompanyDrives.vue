<template>
  <div class="container mt-4">
    <h2>My Placement Drives</h2>
    <router-link to="/company/drives/create" class="btn btn-success mb-3">Create New Drive</router-link>
    <table class="table">
      <thead>
        <tr>
          <th>Job Title</th>
          <th>Description</th>
          <th>Eligibility</th>
          <th>Deadline</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="drive in drives" :key="drive.id">
          <td>{{ drive.job_title }}</td>
          <td>{{ drive.description }}</td>
          <td>{{ drive.eligibility }}</td>
          <td>{{ formatDate(drive.deadline) }}</td>
          <td>{{ drive.status }}</td>
          <td>
            <router-link :to="`/company/drives/${drive.id}/applications`" class="btn btn-info btn-sm me-1">Applications</router-link>
            <router-link v-if="drive.status !== 'closed'" :to="`/company/drives/${drive.id}/edit`" class="btn btn-primary btn-sm me-1">Edit</router-link>
            <button v-if="drive.status !== 'closed'" @click="deleteDrive(drive.id)" class="btn btn-danger btn-sm me-1">Delete</button>
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
  name: 'CompanyDrives',
  data() {
    return {
      drives: []
    }
  },
  mounted() {
    this.fetchDrives()
  },
  methods: {
    async fetchDrives() {
      try {
        const res = await axios.get('/company/drives')
        this.drives = res.data
      } catch (err) {
        console.error(err)
      }
    },
    async deleteDrive(id) {
      if (!confirm('Delete this drive? This action cannot be undone.')) return
      try {
        await axios.delete(`/company/drives/${id}`)
        this.fetchDrives()
      } catch (err) {
        alert('Error deleting drive')
      }
    },
    async closeDrive(id) {
      if (!confirm('Close this drive?')) return
      try {
        await axios.post(`/company/drives/${id}/close`)
        this.fetchDrives()
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
