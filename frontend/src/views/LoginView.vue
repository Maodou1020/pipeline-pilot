<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { login } from '@/auth.js'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const errorMessage = ref(
  route.query.reason === 'session-expired' ? 'Your session expired. Please sign in again.' : '',
)
const isSubmitting = ref(false)

async function handleSubmit() {
  errorMessage.value = ''

  if (username.value.trim() === '') {
    errorMessage.value = 'Please enter the administrator username.'
    return
  }

  if (password.value === '') {
    errorMessage.value = 'Please enter the administrator password.'
    return
  }

  isSubmitting.value = true

  try {
    if (!(await login(username.value, password.value))) {
      errorMessage.value = 'The username or password is incorrect.'
      return
    }

    const redirectPath =
      typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'

    await router.push(redirectPath)
  } catch {
    errorMessage.value = 'Unable to connect to the server. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-panel panel">
      <div class="login-heading">
        <p class="eyebrow">Testing access</p>
        <h1>Administrator sign in</h1>
        <p>PipelinePilot is currently in testing. Access is limited to the administrator.</p>
      </div>

      <form class="login-form" @submit.prevent="handleSubmit">
        <div>
          <label class="field-label" for="username">Username</label>
          <input
            id="username"
            v-model="username"
            class="field-input"
            type="text"
            autocomplete="username"
            placeholder="Enter administrator username"
          />
        </div>

        <div>
          <label class="field-label" for="password">Password</label>
          <input
            id="password"
            v-model="password"
            class="field-input"
            type="password"
            autocomplete="current-password"
            placeholder="Enter administrator password"
          />
        </div>

        <button class="button button-primary" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>

      <p v-if="errorMessage" class="form-error" role="alert">
        {{ errorMessage }}
      </p>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 40px 20px;
  background: #eef2f5;
}

.login-panel {
  width: min(100%, 460px);
  padding: 34px;
}

.login-heading {
  border-bottom: 1px solid #e2e8ee;
  padding-bottom: 22px;
}

.login-heading h1 {
  margin: 0;
  color: #17212b;
  font-size: 1.72rem;
  letter-spacing: 0;
}

.login-heading > p:last-child {
  margin: 10px 0 0;
  color: #647180;
  line-height: 1.55;
}

.login-form {
  display: grid;
  gap: 18px;
  padding-top: 24px;
}

.test-notice {
  display: grid;
  gap: 4px;
  margin-top: 22px;
  border-left: 3px solid #b45309;
  background: #fff8eb;
  color: #5f4930;
  padding: 12px 14px;
  font-size: 0.86rem;
}

.test-notice strong {
  color: #7c3d0b;
}

.login-form .button {
  width: 100%;
  margin-top: 4px;
}

.form-error {
  margin: 16px 0 0;
  border-left: 3px solid #b42318;
  background: #fff1f0;
  color: #8f1d14;
  padding: 10px 12px;
  font-size: 0.9rem;
}
</style>
