<template>
  <div class="container mt-4">
    <h2>Applications for {{ driveTitle }}</h2>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Student Name</th>
          <th>Email</th>
          <th>Contact</th>
          <th>Branch</th>
          <th>Year</th>
          <th>CGPA</th>
          <th>Applied On</th>
          <th>Resume</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="app in applications" :key="app.id">
          <td>{{ app.student_name }}</td>
          <td>{{ app.student_email }}</td>
          <td>{{ app.student_contact }}</td>
          <td>{{ app.student_branch }}</td>
          <td>{{ app.student_year }}</td>
          <td>{{ app.student_cgpa }}</td>
          <td>{{ formatDate(app.application_date) }}</td>
          <td>
            <a v-if="app.resume_path" :href="`/static/uploads/resumes/${app.resume_path}`" target="_blank">View</a>
            <span v-else>No resume</span>
          </td>
          <td>
            <select class="form-select form-select-sm" v-model="app.status" @change="updateStatus(app.id, app.status)">
              <option value="applied">Applied</option>
              <option value="shortlisted">Shortlisted</option>
              <option value="selected">Selected</option>
              <option value="rejected">Rejected</option>
            </select>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from '../plugins/axios'

export default {
  name: 'DriveApplications',
  data() {
    return {
      driveId: this.$route.params.id,
      driveTitle: '',
      applications: []
    }
  },
  mounted() {
    this.fetchApplications()
  },
  methods: {
    async fetchApplications() {
      try {
        const res = await axios.get(`/company/drives/${this.driveId}/applications`)
        // Backend now returns paginated response: { applications, total, pages, current_page }
        this.applications = res.data.applications
        const driveRes = await axios.get(`/company/drives/${this.driveId}`)
        this.driveTitle = driveRes.data.job_title
      } catch (err) {
        console.error(err)
      }
    },
    async updateStatus(appId, newStatus) {
      try {
        await axios.put(`/company/applications/${appId}`, { status: newStatus })
        alert('Status updated')
      } catch (err) {
        alert('Error updating status')
      }
    },
    formatDate(dateStr) {
      const d = new Date(dateStr)
      return d.toLocaleDateString()
    }
  }
}
</script>
