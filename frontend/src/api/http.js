const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api'

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    ...options,
  })

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json') ? await response.json() : null

  if (!response.ok) {
    const error = new Error(data?.error || 'The request failed.')
    error.status = response.status
    error.data = data

    if (response.status === 401 && path !== '/auth/login') {
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }

    throw error
  }

  return data
}
