import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

import { clearAuthentication } from '@/auth.js'

window.addEventListener('auth:unauthorized', () => {
  clearAuthentication()
  router.replace({
    name: 'login',
    query: { reason: 'session-expired' },
  })
})

const app = createApp(App)

app.use(router)

app.mount('#app')
