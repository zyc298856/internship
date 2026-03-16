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
    <!-- Star Decoration -->
    <svg class="bg-star" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C12 5.5 16.5 10 22 10V14C16.5 14 12 18.5 12 24H10C10 18.5 5.5 14 0 14V10C5.5 10 10 5.5 10 0H12Z" />
    </svg>
    <div class="glass-card">
      <div class="brand">
        <h1 class="glow-text">GLM-5 Nexus</h1>
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
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
}

.bg-star {
  position: absolute;
  bottom: 2.5rem;
  right: 2.5rem;
  width: 45px;
  height: 45px;
  color: rgba(200, 220, 240, 0.6);
  filter: drop-shadow(0 0 10px rgba(200, 220, 240, 0.4));
  z-index: 1;
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.glass-card {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 229, 255, 0.3);
  border-radius: 20px;
  padding: 3rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 0 30px rgba(0, 229, 255, 0.15), inset 0 0 20px rgba(0, 229, 255, 0.1);
  transform: translateY(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0 40px rgba(0, 229, 255, 0.25), inset 0 0 30px rgba(0, 229, 255, 0.15);
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
  text-shadow: 0 0 20px rgba(0, 229, 255, 0.6), 0 0 40px rgba(0, 229, 255, 0.3);
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
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.1) !important;
  border: 1px solid rgba(0, 229, 255, 0.4);
  border-radius: 999px; /* Pill shape */
  padding: 0 15px;
}

::v-deep(.modern-input input) {
  color: #fff !important;
  background: transparent !important;
}

::v-deep(.modern-input .el-input__wrapper.is-focus) {
  border-color: #00e5ff;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.3) !important;
}

/* Fix CSS for Chrome autofill overriding dark background */
::v-deep(.modern-input input:-webkit-autofill),
::v-deep(.modern-input input:-webkit-autofill:hover), 
::v-deep(.modern-input input:-webkit-autofill:focus), 
::v-deep(.modern-input input:-webkit-autofill:active) {
    -webkit-text-fill-color: white !important;
    transition: background-color 5000s ease-in-out 0s;
    background-color: transparent !important;
}

.submit-btn {
  background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
  border: none;
  border-radius: 999px;
  font-weight: bold;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
}

.submit-btn:hover {
  box-shadow: 0 0 25px rgba(59, 130, 246, 0.7);
  opacity: 1;
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
