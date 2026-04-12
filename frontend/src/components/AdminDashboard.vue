<template>
  <div class="container mt-4">
    <h2>Admin Dashboard</h2>
    <div class="row">
      <div class="col-md-3 mb-3">
        <div class="card text-white bg-primary">
          <div class="card-body">
            <h5 class="card-title">Students</h5>
            <p class="card-text display-6">{{ stats.total_students }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-white bg-success">
          <div class="card-body">
            <h5 class="card-title">Companies</h5>
            <p class="card-text display-6">{{ stats.total_companies }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-white bg-warning">
          <div class="card-body">
            <h5 class="card-title">Drives</h5>
            <p class="card-text display-6">{{ stats.total_drives }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-white bg-info">
          <div class="card-body">
            <h5 class="card-title">Applications</h5>
            <p class="card-text display-6">{{ stats.total_applications }}</p>
          </div>
        </div>
      </div>
    </div>

    <ul class="nav nav-tabs mt-4" id="adminTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link active" id="companies-tab" data-bs-toggle="tab" data-bs-target="#companies" type="button" role="tab" @click="fetchCompanies">Companies</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="students-tab" data-bs-toggle="tab" data-bs-target="#students" type="button" role="tab" @click="fetchStudents">Students</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="drives-tab" data-bs-toggle="tab" data-bs-target="#drives" type="button" role="tab" @click="fetchDrives">Drives</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="all-applications-tab" data-bs-toggle="tab" data-bs-target="#all-applications" type="button" role="tab" @click="fetchAllApplications">All Applications</button>
      </li>
    </ul>

    <div class="tab-content mt-3">
      <!-- Companies Tab -->
      <div class="tab-pane fade show active" id="companies" role="tabpanel">
        <div class="mb-3">
          <input type="text" v-model="companySearch" @input="searchCompanies" class="form-control" placeholder="Search companies...">
        </div>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Company Name</th>
              <th>Email</th>
              <th>HR Contact</th>
              <th>Approved</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="company in companies" :key="company.user_id">
              <td>{{ company.user_id }}</td>
              <td>{{ company.company_name }}</td>
              <td>{{ company.email }}</td>
              <td>{{ company.hr_contact }}</td>
              <td>{{ company.approved ? 'Yes' : 'No' }}</td>
              <td>{{ company.is_active ? 'Active' : 'Inactive' }}</td>
              <td>
                <button v-if="!company.approved && company.is_active" @click="approveCompany(company.user_id)" class="btn btn-success btn-sm me-1">Approve</button>
                <button v-if="!company.approved && company.is_active" @click="rejectCompany(company.user_id)" class="btn btn-danger btn-sm me-1">Reject</button>
                <button v-if="company.is_active" @click="blacklistCompany(company.user_id)" class="btn btn-warning btn-sm me-1">Blacklist</button>
                <button v-if="!company.is_active" @click="activateCompany(company.user_id)" class="btn btn-secondary btn-sm me-1">Activate</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Students Tab -->
      <div class="tab-pane fade" id="students" role="tabpanel">
        <div class="mb-3">
          <input type="text" v-model="studentSearch" @input="searchStudents" class="form-control" placeholder="Search students...">
        </div>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Contact</th>
              <th>Branch</th>
              <th>Year</th>
              <th>CGPA</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.user_id">
              <td>{{ student.user_id }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.email }}</td>
              <td>{{ student.contact }}</td>
              <td>{{ student.branch }}</td>
              <td>{{ student.year }}</td>
              <td>{{ student.cgpa }}</td>
              <td>{{ student.is_active ? 'Active' : 'Inactive' }}</td>
              <td>
                <button v-if="student.is_active" @click="blacklistStudent(student.user_id)" class="btn btn-warning btn-sm me-1">Blacklist</button>
                <button v-if="!student.is_active" @click="activateStudent(student.user_id)" class="btn btn-secondary btn-sm me-1">Activate</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Drives Tab -->
      <div class="tab-pane fade" id="drives" role="tabpanel">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Company</th>
              <th>Job Title</th>
              <th>Deadline</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drive in drives" :key="drive.id">
              <td>{{ drive.id }}</td>
              <td>{{ drive.company_name }}</td>
              <td>{{ drive.job_title }}</td>
              <td>{{ formatDate(drive.deadline) }}</td>
              <td>{{ drive.status }}</td>
              <td>
                <button v-if="drive.status === 'pending'" @click="approveDrive(drive.id)" class="btn btn-success btn-sm me-1">Approve</button>
                <button v-if="drive.status === 'pending'" @click="rejectDrive(drive.id)" class="btn btn-danger btn-sm me-1">Reject</button>
                <button v-if="drive.status === 'approved'" @click="closeDrive(drive.id)" class="btn btn-warning btn-sm me-1">Close</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- All Applications Tab -->
      <div class="tab-pane fade" id="all-applications" role="tabpanel">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Student</th>
              <th>Email</th>
              <th>Company</th>
              <th>Job Title</th>
              <th>Applied On</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in allApplications" :key="app.id">
              <td>{{ app.student_name }}</td>
              <td>{{ app.student_email }}</td>
              <td>{{ app.company_name }}</td>
              <td>{{ app.job_title }}</td>
              <td>{{ formatDate(app.applied_on) }}</td>
              <td>{{ app.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '../plugins/axios'
import _ from 'lodash'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {
        total_students: 0,
        total_companies: 0,
        total_drives: 0,
        total_applications: 0
      },
      companies: [],
      students: [],
      drives: [],
      allApplications: [],
      companySearch: '',
      studentSearch: ''
    }
  },
  mounted() {
    this.fetchDashboardStats()
    this.fetchCompanies()
    this.fetchStudents()
    this.fetchDrives()
    this.fetchAllApplications()
  },
  methods: {
    async fetchDashboardStats() {
      try {
        const res = await axios.get('/admin/dashboard')
        this.stats = res.data
      } catch (err) {
        console.error(err)
      }
    },
    async fetchCompanies() {
      try {
        const res = await axios.get('/admin/companies', { params: { search: this.companySearch } })
        this.companies = res.data
      } catch (err) {
        console.error(err)
      }
    },
    async fetchStudents() {
      try {
        const res = await axios.get('/admin/students', { params: { search: this.studentSearch } })
        this.students = res.data
      } catch (err) {
        console.error(err)
      }
    },
    async fetchDrives() {
      try {
        const res = await axios.get('/admin/drives')
        this.drives = res.data
      } catch (err) {
        console.error(err)
      }
    },
    async fetchAllApplications() {
      try {
        const res = await axios.get('/admin/applications', { params: { page: 1, per_page: 50 } })
        this.allApplications = res.data.applications
      } catch (err) {
        console.error(err)
      }
    },
    searchCompanies: _.debounce(function() {
      this.fetchCompanies()
    }, 500),
    searchStudents: _.debounce(function() {
      this.fetchStudents()
    }, 500),
    async approveCompany(id) {
      try {
        await axios.post(`/admin/companies/${id}/approve`)
        this.fetchCompanies()
      } catch (err) {
        alert('Error approving company')
      }
    },
    async rejectCompany(id) {
      if (!confirm('Reject and delete this company?')) return
      try {
        await axios.delete(`/admin/companies/${id}/reject`)
        this.fetchCompanies()
      } catch (err) {
        alert('Error rejecting company')
      }
    },
    async blacklistCompany(id) {
      if (!confirm('Blacklist this company?')) return
      try {
        await axios.post(`/admin/companies/${id}/blacklist`)
        this.fetchCompanies()
      } catch (err) {
        alert('Error blacklisting company')
      }
    },
    async activateCompany(id) {
      try {
        await axios.post(`/admin/companies/${id}/activate`)
        this.fetchCompanies()
      } catch (err) {
        alert('Error activating company')
      }
    },
    async blacklistStudent(id) {
      if (!confirm('Blacklist this student?')) return
      try {
        await axios.post(`/admin/students/${id}/blacklist`)
        this.fetchStudents()
      } catch (err) {
        alert('Error blacklisting student')
      }
    },
    async activateStudent(id) {
      try {
        await axios.post(`/admin/students/${id}/activate`)
        this.fetchStudents()
      } catch (err) {
        alert('Error activating student')
      }
    },
    async approveDrive(id) {
      try {
        await axios.post(`/admin/drives/${id}/approve`)
        this.fetchDrives()
      } catch (err) {
        alert('Error approving drive')
      }
    },
    async rejectDrive(id) {
      try {
        await axios.post(`/admin/drives/${id}/reject`)
        this.fetchDrives()
      } catch (err) {
        alert('Error rejecting drive')
      }
    },
    async closeDrive(id) {
      try {
        await axios.post(`/admin/drives/${id}/close`)
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
