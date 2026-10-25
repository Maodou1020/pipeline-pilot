<script setup>
import { isAuthenticated } from '@/auth.js'
</script>

<template>
  <main class="not-found-page">
    <section class="not-found-panel panel">
      <p class="eyebrow">404 error</p>
      <h1>Page not found</h1>
      <p>The address may be incorrect, or the page may have moved.</p>
      <RouterLink
        class="button button-primary"
        :to="isAuthenticated() ? { name: 'dashboard' } : { name: 'login' }"
      >
        {{ isAuthenticated() ? 'Return to dashboard' : 'Go to sign in' }}
      </RouterLink>
    </section>
  </main>
</template>

<style scoped>
.not-found-page {
  display: grid;
  min-height: calc(100vh - 67px);
  place-items: center;
  padding: 40px 20px;
}

.not-found-panel {
  width: min(100%, 520px);
  padding: 34px;
  text-align: center;
}

h1 {
  margin: 0;
  color: #17212b;
  font-size: 2rem;
}

.not-found-panel > p:not(.eyebrow) {
  margin: 12px 0 24px;
  color: #647180;
  line-height: 1.6;
}
</style>
