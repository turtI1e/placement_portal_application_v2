<template>
  <div class="container mt-4">
    <h2>Approved Placement Drives</h2>
    <div class="mb-3">
      <input type="text" v-model="search" @input="searchDrives" class="form-control" placeholder="Search by job title, company, or eligibility...">
    </div>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Company</th>
          <th>Job Title</th>
          <th>Description</th>
          <th>Eligibility</th>
          <th>Deadline</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="drive in drives" :key="drive.id">
          <td>{{ drive.company_name }}</td>
          <td>{{ drive.job_title }}</td>
          <td>{{ drive.description }}</td>
          <td>{{ drive.eligibility }}</td>
          <td>{{ formatDate(drive.deadline) }}</td>
          <td>
            <button v-if="!drive.applied" @click="apply(drive.id)" class="btn btn-primary btn-sm" :disabled="applying === drive.id">
              {{ applying === drive.id ? 'Applying...' : 'Apply' }}
            </button>
            <span v-else class="badge bg-success">Applied</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from '../plugins/axios'
import _ from 'lodash'

export default {
  name: 'StudentDrives',
  data() {
    return {
      drives: [],
      search: '',
      applying: null
    }
  },
  mounted() {
    this.fetchDrives()
  },
  methods: {
    async fetchDrives() {
      try {
        const res = await axios.get('/student/drives', { params: { search: this.search } })
        this.drives = res.data
      } catch (err) {
        console.error(err)
      }
    },
    searchDrives: _.debounce(function() {
      this.fetchDrives()
    }, 500),
    async apply(driveId) {
      this.applying = driveId
      try {
        await axios.post(`/student/drives/${driveId}/apply`)
        alert('Application submitted')
        this.fetchDrives()
      } catch (err) {
        alert(err.response?.data?.msg || 'Application failed')
      } finally {
        this.applying = null
      }
    },
    formatDate(dateStr) {
      const d = new Date(dateStr)
      return d.toLocaleDateString()
    }
  }
}
</script>
