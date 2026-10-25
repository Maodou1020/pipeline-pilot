import { apiRequest } from '@/api/http.js'

export function getPipelines() {
  return apiRequest('/pipelines')
}

export function getPipeline(pipelineId) {
  return apiRequest(`/pipelines/${pipelineId}`)
}

export function createPipeline(name) {
  return apiRequest('/pipelines', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name }),
  })
}

export function updatePipeline(pipelineId, name) {
  return apiRequest(`/pipelines/${pipelineId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name }),
  })
}

export function deletePipeline(pipelineId) {
  return apiRequest(`/pipelines/${pipelineId}`, {
    method: 'DELETE',
  })
}

export function validatePipeline(pipelineId) {
  return apiRequest(`/pipelines/${pipelineId}/validate`, {
    method: 'POST',
  })
}

export function simulatePipeline(pipelineId, workerCount) {
  return apiRequest(`/pipelines/${pipelineId}/simulate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ worker_count: workerCount }),
  })
}
