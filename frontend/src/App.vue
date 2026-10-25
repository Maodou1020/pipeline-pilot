<script setup>
import { useRouter } from 'vue-router'
import { RouterLink, RouterView } from 'vue-router'

import { authenticatedUser, logout } from '@/auth.js'

const router = useRouter()

async function handleLogout() {
  try {
    await logout()
  } finally {
    await router.replace({ name: 'login' })
  }
}
</script>

<template>
  <header v-if="authenticatedUser" class="app-header">
    <nav class="app-nav" aria-label="Primary navigation">
      <RouterLink class="brand" to="/">
        <span class="brand-mark">PP</span>
        <span>PipelinePilot</span>
      </RouterLink>

      <div class="nav-links">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <span class="admin-name">{{ authenticatedUser }}</span>
        <button class="logout-button" type="button" @click="handleLogout">Sign out</button>
      </div>
    </nav>
  </header>

  <RouterView />
</template>

<style scoped>
nav {
  display: flex;
}

.app-header {
  position: sticky;
  z-index: 20;
  top: 0;
  border-bottom: 1px solid #dce3e9;
  background: rgba(255, 255, 255, 0.96);
}

.app-nav {
  width: min(1180px, calc(100% - 40px));
  min-height: 66px;
  align-items: center;
  justify-content: space-between;
  margin: 0 auto;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #17212b;
  font-weight: 800;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 6px;
  background: #17324d;
  color: #ffffff;
  font-size: 0.72rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-links a {
  border-radius: 5px;
  color: #52606d;
  padding: 8px 11px;
  font-size: 0.9rem;
  font-weight: 650;
  text-decoration: none;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  background: #eef3f6;
  color: #17212b;
}

.admin-name {
  margin-left: 6px;
  color: #0f766e;
  font-size: 0.82rem;
  font-weight: 750;
}

.logout-button {
  border: 1px solid #b8c5d0;
  border-radius: 5px;
  background: #ffffff;
  color: #52606d;
  padding: 8px 11px;
  font-size: 0.9rem;
  font-weight: 650;
}

.logout-button:hover {
  border-color: #8fa1b2;
  background: #f8fafc;
  color: #17212b;
}

@media (max-width: 640px) {
  .app-nav {
    width: min(100% - 24px, 1180px);
  }

  .brand > span:last-child {
    display: none;
  }

  .nav-links {
    gap: 2px;
  }

  .nav-links a {
    padding: 8px;
    font-size: 0.82rem;
  }

  .admin-name {
    display: none;
  }

  .logout-button {
    padding: 8px;
    font-size: 0.82rem;
  }
}
</style>
