<template>
  <div class="admin-login">
    <div class="login-card">
      <h2>Admin Login</h2>
      <form @submit.prevent="onSubmit">
        <label>
          Username
          <input v-model="username" type="text" autocomplete="username" />
        </label>
        <label>
          Password
          <input v-model="password" type="password" autocomplete="current-password" />
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Log in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { listDocuments } from '../api/admin'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  const creds = btoa(`${username.value}:${password.value}`)
  sessionStorage.setItem('adminCredentials', creds)
  try {
    await listDocuments()
    router.push('/admin')
  } catch {
    sessionStorage.removeItem('adminCredentials')
    error.value = 'Invalid credentials'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login {
  display: flex;
  justify-content: center;
  padding: 60px 24px;
}
.login-card {
  background: var(--panel);
  border-radius: 18px;
  padding: 32px;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 20px 60px rgba(7, 10, 18, 0.35);
}
.login-card h2 {
  margin: 0 0 24px;
  font-family: "Fraunces", serif;
  color: var(--ink);
}
label {
  display: block;
  margin-bottom: 16px;
  color: #111;
  font-size: 1.05rem;
}
input {
  display: block;
  width: 100%;
  margin-top: 6px;
  padding: 10px 12px;
  border: 1px solid #c9c3b8;
  border-radius: 8px;
  background: #fff;
  color: var(--ink);
  font-size: 1.05rem;
  box-sizing: border-box;
}
input:focus {
  outline: none;
  border-color: var(--accent-2);
}
button {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  color: #fff;
  font-weight: 600;
  font-size: 1.05rem;
  cursor: pointer;
  transition: opacity 0.2s;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #b02a37;
  font-size: 1rem;
  margin: 0 0 12px;
}
</style>
