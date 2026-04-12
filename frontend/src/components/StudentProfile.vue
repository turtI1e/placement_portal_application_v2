<template>
  <div class="container mt-4">
    <h2>Student Profile</h2>
    <form @submit.prevent="updateProfile">
      <div class="mb-3">
        <label for="name" class="form-label">Full Name</label>
        <input type="text" class="form-control" id="name" v-model="form.name" required>
      </div>
      <div class="mb-3">
        <label for="contact" class="form-label">Contact</label>
        <input type="text" class="form-control" id="contact" v-model="form.contact">
      </div>
      <div class="mb-3">
        <label for="branch" class="form-label">Branch</label>
        <input type="text" class="form-control" id="branch" v-model="form.branch">
      </div>
      <div class="mb-3">
        <label for="year" class="form-label">Year</label>
        <input type="number" class="form-control" id="year" v-model="form.year">
      </div>
      <div class="mb-3">
        <label for="cgpa" class="form-label">CGPA</label>
        <input type="number" step="0.01" class="form-control" id="cgpa" v-model="form.cgpa">
      </div>
      <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? 'Saving...' : 'Save Changes' }}</button>
    </form>
    <hr>
    <h3>Resume</h3>
    <div v-if="resumePath">
      <p>Current resume: <a :href="`/static/uploads/resumes/${resumePath}`" target="_blank">View</a></p>
    </div>
    <form @submit.prevent="uploadResume" enctype="multipart/form-data">
      <div class="mb-3">
        <label for="resume" class="form-label">Upload New Resume (PDF/DOC/DOCX)</label>
        <input type="file" class="form-control" id="resume" ref="resumeFile" accept=".pdf,.doc,.docx">
      </div>
      <button type="submit" class="btn btn-secondary" :disabled="uploading">{{ uploading ? 'Uploading...' : 'Upload Resume' }}</button>
    </form>
  </div>
</template>

<script>
import axios from '../plugins/axios'

export default {
  name: 'StudentProfile',
  data() {
    return {
      form: {
        name: '',
        contact: '',
        branch: '',
        year: '',
        cgpa: ''
      },
      resumePath: '',
      loading: false,
      uploading: false
    }
  },
  mounted() {
    this.fetchProfile()
  },
  methods: {
    async fetchProfile() {
      try {
        const res = await axios.get('/student/profile')
        this.form = res.data
        this.resumePath = res.data.resume_path
      } catch (err) {
        console.error(err)
      }
    },
    async updateProfile() {
      this.loading = true
      try {
        await axios.put('/student/profile', this.form)
        alert('Profile updated')
        this.$router.push('/student/dashboard')
      } catch (err) {
        alert('Error updating profile')
      } finally {
        this.loading = false
      }
    },
    async uploadResume() {
      const file = this.$refs.resumeFile.files[0]
      if (!file) return
      const formData = new FormData()
      formData.append('resume', file)
      this.uploading = true
      try {
        const res = await axios.post('/student/resume', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        this.resumePath = res.data.resume_path
        alert('Resume uploaded')
      } catch (err) {
        alert('Upload failed')
      } finally {
        this.uploading = false
      }
    }
  }
}
</script>
