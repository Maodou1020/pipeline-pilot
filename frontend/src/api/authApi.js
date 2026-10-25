import { apiRequest } from '@/api/http.js'

export function loginAdmin(username, password) {
  return apiRequest('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: username.trim(),
      password,
    }),
  })
}

export function logoutAdmin() {
  return apiRequest('/auth/logout', {
    method: 'POST',
  })
}

export function getAuthSession() {
  return apiRequest('/auth/session')
}
