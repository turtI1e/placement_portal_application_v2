<template>
  <div class="container mt-4">
    <h2>Student Dashboard</h2>
    <div class="row">
      <div class="col-md-6">
        <div class="card mb-3">
          <div class="card-body">
            <h5 class="card-title">Welcome, {{ student.name }}</h5>
            <p class="card-text">Email: {{ student.email }}</p>
            <p class="card-text">Branch: {{ student.branch }} | Year: {{ student.year }} | CGPA: {{ student.cgpa }}</p>
            <router-link to="/student/profile" class="btn btn-primary">Edit Profile</router-link>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-info">
          <div class="card-body">
            <h5 class="card-title">Approved Drives</h5>
            <p class="display-6">{{ approvedDrivesCount }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-success">
          <div class="card-body">
            <h5 class="card-title">Your Applications</h5>
            <p class="display-6">{{ appliedDrivesCount }}</p>
          </div>
        </div>
      </div>
    </div>
    <div class="mt-4">
      <router-link to="/student/drives" class="btn btn-success me-2">Browse Drives</router-link>
      <router-link to="/student/applications" class="btn btn-info">View Applications</router-link>
    </div>
  </div>
</template>

<script>
import axios from '../plugins/axios'

export default {
  name: 'StudentDashboard',
  data() {
    return {
      student: {},
      approvedDrivesCount: 0,
      appliedDrivesCount: 0
    }
  },
  mounted() {
    this.fetchDashboard()
  },
  methods: {
    async fetchDashboard() {
      try {
        const res = await axios.get('/student/dashboard')
        this.student = res.data.student
        this.approvedDrivesCount = res.data.approved_drives_count
        this.appliedDrivesCount = res.data.applied_drives_count
      } catch (err) {
        console.error(err)
      }
    }
  }
}
</script>
