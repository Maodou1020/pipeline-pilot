import { apiRequest } from '@/api/http.js'

export function createTask(pipelineId, task) {
  return apiRequest(`/pipelines/${pipelineId}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: task.name,
      duration: task.duration,
      dependencies: task.dependencies,
    }),
  })
}

export function updateTask(taskId, task) {
  return apiRequest(`/tasks/${taskId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: task.name,
      duration: task.duration,
      dependencies: task.dependencies,
    }),
  })
}

export function deleteTask(taskId) {
  return apiRequest(`/tasks/${taskId}`, {
    method: 'DELETE',
  })
}
