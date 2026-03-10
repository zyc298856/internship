<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../services/api'

const router = useRouter()
const isLoginMode = ref(true)

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)

const handleSubmit = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('Please enter username and password')
    return
  }
  
  loading.value = true
  try {
    if (isLoginMode.value) {
      // Setup payload using application/x-www-form-urlencoded for OAuth2
      const formData = new URLSearchParams()
      formData.append('username', form.username)
      formData.append('password', form.password)
      
      const res = await api.post('/auth/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      localStorage.setItem('token', res.data.access_token)
      ElMessage.success('Login Successful')
      router.push('/')
    } else {
      await api.post('/auth/register', { username: form.username, password: form.password })
      ElMessage.success('Registration successful. You can now login.')
      isLoginMode.value = true
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || 'Authentication failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrapper">
    <div class="glass-card">
      <div class="brand">
        <h1 class="glow-text">GLM-4V-Plus Nexus</h1>
        <p>Multimodal Next-Gen AI</p>
      </div>
      
      <el-form class="auth-form" @submit.prevent>
        <el-input 
          v-model="form.username" 
          placeholder="Username" 
          size="large"
          class="modern-input"
        >
          <template #prefix><i class="el-icon-user"></i></template>
        </el-input>
        
        <el-input 
          v-model="form.password" 
          type="password" 
          placeholder="Password" 
          size="large" 
          show-password
          class="modern-input"
        >
          <template #prefix><i class="el-icon-lock"></i></template>
        </el-input>
        
        <el-button 
          type="primary" 
          size="large" 
          class="submit-btn" 
          :loading="loading"
          @click="handleSubmit"
        >
          {{ isLoginMode ? 'Enter Nexus' : 'Initialize Account' }}
        </el-button>
        
        <div class="toggle-mode">
          <span @click="isLoginMode = !isLoginMode">
            {{ isLoginMode ? 'Create new identity?' : 'Already have an identity?' }}
          </span>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.auth-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 3rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  transform: translateY(0);
  transition: transform 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-5px);
}

.brand {
  text-align: center;
  margin-bottom: 2.5rem;
}

.glow-text {
  font-size: 2.5rem;
  color: #fff;
  margin: 0;
  font-weight: 800;
  text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
  letter-spacing: -1px;
}

.brand p {
  color: #a0aec0;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  letter-spacing: 1px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

::v-deep(.modern-input .el-input__wrapper) {
  background: rgba(0, 0, 0, 0.2);
  box-shadow: none !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

::v-deep(.modern-input input) {
  color: #fff !important;
}

::v-deep(.modern-input .el-input__wrapper.is-focus) {
  border-color: #00e5ff;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.3) !important;
}

.submit-btn {
  background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
  border: none;
  border-radius: 10px;
  font-weight: bold;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  box-shadow: 0 0 20px rgba(0, 114, 255, 0.6);
  opacity: 0.9;
}

.toggle-mode {
  text-align: center;
  margin-top: 1rem;
}

.toggle-mode span {
  color: #cbd5e0;
  font-size: 0.85rem;
  cursor: pointer;
  transition: color 0.3s ease;
}

.toggle-mode span:hover {
  color: #00e5ff;
  text-decoration: underline;
}
</style>
