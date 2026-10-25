import { readonly, ref } from 'vue'

import { getAuthSession, loginAdmin, logoutAdmin } from '@/api/authApi.js'

const currentUser = ref(null)
let sessionChecked = false

export const authenticatedUser = readonly(currentUser)

export async function login(username, password) {
  try {
    const data = await loginAdmin(username, password)
    currentUser.value = data.username
    sessionChecked = true
    return true
  } catch (error) {
    if (error.status === 401) {
      return false
    }

    throw error
  }
}

export async function logout() {
  try {
    await logoutAdmin()
  } finally {
    currentUser.value = null
    sessionChecked = true
  }
}

export async function restoreSession() {
  if (sessionChecked) {
    return isAuthenticated()
  }

  try {
    const data = await getAuthSession()
    currentUser.value = data.authenticated ? data.username : null
    return data.authenticated
  } catch {
    currentUser.value = null
    return false
  } finally {
    sessionChecked = true
  }
}

export function isAuthenticated() {
  return currentUser.value !== null
}

export function clearAuthentication() {
  currentUser.value = null
  sessionChecked = true
}
